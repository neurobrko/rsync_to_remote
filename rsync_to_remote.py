#!/usr/bin/env python3

from subprocess import run, PIPE
from error_handler import RepeatingKeyError, BadFileSyncDefinition
import argparse
from os import path
import logging
from time import strftime, sleep
from pytimedinput import timedKey
import yaml

# define paths
# TODO: delete log files older then x days.
script_root = path.dirname(path.realpath(__file__))
conf_file = path.join(script_root, "sync_conf.yaml")
filemap_file = path.join(script_root, "file_map.yaml")

# import configuration variables
with open(conf_file, "r") as f:
    config = yaml.safe_load(f)

# remove GUI variables
config.pop("gui")

# set empty variable. Otherwise, pyCharm will report unresolved reference :(
host = username = port = local_root_dir = ""
rsync_options = []
VM_check_timeout = result_timeout = default_dir = date_format = ""
project = file_keys = ""
sync_all = False
GN = GB = RN = RB = CN = CB = WU = BLD = UND = RST = ""
for vals in config.values():
    vars().update(vals)

# invoke logger
LOGGER = logging.getLogger()

log_filename = f"rsync_to_remote-{strftime('%y%m%d')}.log"
path.join(script_root, "log", log_filename)
logging.basicConfig(
    format="%(levelname)s: [:%(lineno)d] %(message)s",
    datefmt=date_format,
    filename=path.join(script_root, "log", log_filename),
    level=logging.INFO,
)

# TODO: think about adding dict for rsync settings to use it as set of rules invoked by dict key. \
#  It would probably mean seriously rebuilding this script and GUI...
# OVERRIDE SETTINGS FOR TESTING
# host = "localhost"
# username = "marpauli"
# port = "22"
# rsync_options = ["-rtvz", "--progress", "-e", f"ssh -p {port}"]
# local_root_dir = ""
# project = "test"

# set-up arg parser
ap = argparse.ArgumentParser()
ap.add_argument("-r", "--remote", help="Remote host for synchronization")
ap.add_argument("-u", "--username", help="Remote username")
ap.add_argument("-s", "--ssh_port", help="SSH port")
ap.add_argument("-l", "--local_root_dir", help="Root directory for source files")
ap.add_argument("-vt", "--vm_timeout", help="Timeout to check VM info")
ap.add_argument("-rt", "--result_timeout", help="Timeout to check script output")
ap.add_argument("-t", "--timestamp", help="Timestamp format for logging")
ap.add_argument(
    "-a", "--sync_all", help="Sync all files from all projects", action="store_true"
)
ap.add_argument("-p", "--project", help="Sync all files from project")
ap.add_argument(
    "-f", "--files", help="Sync selected files. No spaces, comma as separator."
)

args = ap.parse_args()

# override settings, if set from cli
if args.remote:
    host = args.remote
if args.username:
    username = args.username
if args.ssh_port:
    port = args.ssh_port
    # if port is specified in CLI, alter rsync_options!
    rsync_options[-1] = f"ssh -p {port}"
if args.local_root_dir:
    local_root_dir = args.local_root_dir
if args.vm_timeout:
    VM_check_timeout = int(args.vm_timeout)
if args.result_timeout:
    result_timeout = int(args.result_timeout)
if args.timestamp:
    date_format = args.timestamp
if args.sync_all:
    sync_all = True
if args.project:
    project = args.project
if args.files:
    file_keys = [int(file) for file in args.files.split(",")]

with open(filemap_file, "r") as f:
    file_map = yaml.safe_load(f)


def check_map_keys(filemap: dict) -> dict:
    all_maps = {}
    maps_length = 0
    for maps in filemap.values():
        new_maps = {k: v for k, v in maps.items()}
        maps_length += len(new_maps)
        all_maps.update(new_maps)
    if maps_length != len(all_maps):
        raise RepeatingKeyError
    return all_maps


def get_project_maps(filemap: dict, project: str) -> dict:
    return filemap[project]


def run_rsync(filepaths: list, counter: int):
    # global rsync_options
    print(f"{GN}[{counter}]{RST}")
    print(f"{CB}local file: {RST}{WU}{filepaths[0]}{RST}")
    print(f"{CB}remote file: {RST}{WU}{filepaths[1]}{RST}")
    to_log = f"\n*_* [{counter}] *_*\nsource: {filepaths[0]}\ntarget: {filepaths[1]}\nrsync output:"
    try:
        output = run(
            ["rsync"]
            + rsync_options
            + [
                path.join(local_root_dir, filepaths[0]),
                f"{username}@{host}:{filepaths[1]}",
            ],
            stdout=PIPE,
            text=True,
        ).stdout
        to_log = "\n".join([to_log, output])
        LOGGER.info(to_log)
        counter += 1
        return counter
    except Exception as err:
        print(f"{RB}Something went wrong! {err}{RST}")
        # to_log = "\n".join([to_log, err])
    LOGGER.info(to_log)


def synchronize_files(all_maps):
    # decide what to sync based on settings
    if sync_all:
        i = 1
        for paths in all_maps.values():
            i = run_rsync(paths, i)
        return i
    elif project:
        file_maps = get_project_maps(file_map, project)
        i = 1
        for paths in file_maps.values():
            # print(paths)
            i = run_rsync(paths, i)
        return i
    elif len(file_keys) > 0:
        i = 1
        for key in file_keys:
            i = run_rsync(all_maps[key], i)
        return i
    else:
        raise BadFileSyncDefinition


def main():
    print("".join([BLD, "> Sync files to remote VM <".center(80, "="), RST]))
    LOGGER.info("> SYNC START <".center(50, "="))
    LOGGER.info(f"timestamp: {strftime(date_format)}")
    # Check for repeating keys in file map projects
    try:
        all_maps = check_map_keys(file_map)
        LOGGER.info("File map keys OK!")
    except RepeatingKeyError:
        msg = "File map contains repeating keys!"
        print(msg)
        LOGGER.error(msg)
        exit()

    # display info about VM
    print(f"{BLD}ssh: {RB}{username}@{host}:{port}{RST}")
    LOGGER.info(f"ssh: {host}:{port}")
    print("Fetching remote hostname...")
    hostname = run(
        ["ssh", "-p", f"{port}", f"{username}@{host}", "echo", "$HOSTNAME"],
        stdout=PIPE,
    ).stdout.decode("utf-8")
    print(f"{BLD}remote hostname: {RB}{hostname}{RST}")
    LOGGER.info(f"remote hostname: {hostname.strip()}")

    # give user few seconds to check VM settings
    # TODO: add countdown
    if VM_check_timeout:
        user_text, timed_out = timedKey(
            f"Correct VM? (Wait for {VM_check_timeout} s.) [y/n]: ",
            timeout=VM_check_timeout,
            allowCharacters="yYnN",
        )
        if timed_out:
            print("Continue synchronization!")
            LOGGER.info("VM check: OK! (w/o user interaction)")
            i = synchronize_files(all_maps)
        else:
            if user_text in ["y", "Y"]:
                LOGGER.info("VM check: OK!")
                i = synchronize_files(all_maps)
            else:
                print("Synchronization canceled. Check WM info.")
                LOGGER.info("VM check: Synchronization canceled by user.")
                LOGGER.info("".join(["> SYNC END <".center(50, "="), "\n\n"]))
                exit()
    else:
        i = synchronize_files(all_maps)

    print(f"{BLD}\nSynced file(s) count: {RST}{RB}{i-1}{RST}\n")
    LOGGER.info(f"\nSynced file(s) count: {i-1}")
    LOGGER.info("".join(["> SYNC END <".center(50, "="), "\n\n"]))

    if result_timeout:
        for x in range(result_timeout):
            print(
                f"{RB}Press Ctrl+C to exit or script will exit in: {(result_timeout - x)} s...{RST}",
                end=" \r",
            )
            sleep(1)
    print(f"{GB}GoodBye!{RST}", " " * 70)
    sleep(1)


if __name__ == "__main__":
    path.join(script_root, "log", log_filename)
    main()
