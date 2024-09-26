#!/usr/bin/env python

import sync_conf as sc
from subprocess import run, PIPE
from error_handler import RepeatingKeyError, BadFileSyncDefinition
import argparse
from os import path
import logging
from time import strftime, sleep
from pytimedinput import timedKey

# invoke logger
LOGGER = logging.getLogger()
# TODO: delete log files older then x days.
script_root = path.dirname(path.realpath(__file__))

log_filename = f"rsync_to_remote-{strftime('%y%m%d')}.log"
logging.basicConfig(
    format="%(levelname)s: [:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    filename=path.join(script_root, "log", log_filename),
    level=logging.INFO,
)

# OVERRIDE SETTINGS FOR TESTING
sc.host = "localhost"
sc.username = "marpauli"
sc.port = "22"
sc.rsync_options = ["-rtvz", "--progress", "-e", f"ssh -p {sc.port}"]
sc.local_root_dir = ""
sc.project = "test"

# set-up arg parser
ap = argparse.ArgumentParser()
ap.add_argument("-r", "--remote", help="Remote host for synchronization")
ap.add_argument("-u", "--username", help="Remote username")
ap.add_argument("-ha", "--host_address", help="Host address part of IP")
ap.add_argument("-s", "--ssh_port", help="SSH port")
ap.add_argument("-l", "--local_root_dir", help="Root directory for source files")
ap.add_argument("-vt", "--vm_timeout", help="Timeout to check VM info", type=int)
ap.add_argument(
    "-rt", "--result_timeout", help="Timeout to check script output", type=int
)
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
    sc.host = args.remote
if args.username:
    sc.username = args.username
if args.host_address:
    sc.host_address = args.host_address
if args.ssh_port:
    sc.port = args.ssh_port
if args.local_root_dir:
    sc.local_root_dir = args.local_root_dir
if args.vm_timeout:
    sc.VM_check_timeout = args.vm_timeoout
if args.result_timeout:
    sc.result_timeout = args.result_timeout
if args.sync_all:
    sc.sync_all = True
if args.project:
    sc.project = args.project
if args.files:
    sc.file_keys = [int(file) for file in args.files.split(",")]


def check_map_keys(file_map: dict) -> dict:
    all_maps = {}
    maps_length = 0
    for maps in file_map.values():
        new_maps = {k: v for k, v in maps.items()}
        maps_length += len(new_maps)
        all_maps.update(new_maps)
    if maps_length != len(all_maps):
        raise RepeatingKeyError
    return all_maps


def get_project_maps(file_map: dict, project: str) -> dict:
    return file_map[project]


def run_cmd(cmd_list: list):
    run(cmd_list)


def run_rsync(filepaths: list, counter: int):
    print(f"{sc.GN}[{counter}]{sc.RST}")
    print(f"{sc.CB}local file: {sc.RST}{sc.WU}{filepaths[0]}{sc.RST}")
    print(f"{sc.CB}remote file: {sc.RST}{sc.WU}{filepaths[1]}{sc.RST}")
    to_log = f"\n*_* [{counter}] *_*\nsource: {filepaths[0]}\ntarget: {filepaths[1]}\nrsync output:"
    try:
        output = run(
            ["rsync"]
            + sc.rsync_options
            + [
                path.join(sc.local_root_dir, filepaths[0]),
                f"{sc.username}@{sc.host}:{filepaths[1]}",
            ],
            stdout=PIPE,
        ).stdout.decode("utf-8")
        to_log = "\n".join([to_log, output])
        LOGGER.info(to_log)
        counter += 1
        return counter
    except Exception as err:
        print(f"Something went wrong!{err}")
        to_log = "\n".join([to_log, err])
    LOGGER.info(to_log)


def synchronize_files(all_maps):
    # decide what to sync based on settings
    if sc.sync_all:
        for paths in all_maps.values():
            print(paths)
            # run_rsync(paths)
    elif sc.project:
        file_maps = get_project_maps(sc.file_map, sc.project)
        i = 1
        for paths in file_maps.values():
            # print(paths)
            i = run_rsync(paths, i)
        return i

    elif len(sc.file_keys) > 0:
        for key in sc.file_keys:
            print(all_maps[key])
            # run_rsync(all_maps[key])
    else:
        raise BadFileSyncDefinition


def main():
    print("".join([sc.BLD, "> Sync files to remote VM <".center(80, "="), sc.RST]))
    LOGGER.info("> SYNC START <".center(50, "="))
    LOGGER.info(f"timestamp: {strftime('%Y-%m-%d %H:%M:%S')}")
    # Check for repeating keys in file map projects
    try:
        all_maps = check_map_keys(sc.file_map)
        LOGGER.info("File map keys OK!")
    except RepeatingKeyError:
        msg = "File map contains repeating keys!"
        print(msg)
        LOGGER.error(msg)
        exit()

    # display info about VM
    print(f"{sc.BLD}VM IP: {sc.RB}10.0.13.{sc.host_address}{sc.RST}")
    LOGGER.info(f"VM IP: 10.0.13.{sc.host_address}")
    print(f"{sc.BLD}ssh: {sc.RB}{sc.host}:{sc.port}{sc.RST}")
    LOGGER.info(f"ssh: {sc.host}:{sc.port}")
    print("Fetching remote hostname...")
    hostname = run(
        ["ssh", "-p", f"{sc.port}", f"{sc.username}@{sc.host}", "echo", "$HOSTNAME"],
        stdout=PIPE,
    ).stdout.decode("utf-8")
    print(f"{sc.BLD}remote hostname: {sc.RB}{hostname}{sc.RST}")
    LOGGER.info(f"remote hostname: {hostname.strip()}")

    # give user few seconds to check VM settings
    # TODO: add countdown
    user_text, timed_out = timedKey(
        f"Correct VM? (Wait for {sc.VM_check_timeout} s.) [y/n]: ",
        timeout=sc.VM_check_timeout,
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

    print(f"{sc.BLD}Synced file(s) count: {sc.RST}{sc.RB}{i-1}{sc.RST}")
    LOGGER.info(f"\nSynced file(s) count: {i-1}")
    LOGGER.info("".join(["> SYNC END <".center(50, "="), "\n\n"]))

    for x in range(sc.result_timeout):
        print(
            f"{sc.RB}Press Ctrl+C to exit or script will exit in: {(sc.result_timeout - x)} s...{sc.RST}",
            end=" \r",
        )
        sleep(1)
    print(f"{sc.GB}GoodBye!{sc.RST}", " " * 70)
    sleep(1)


if __name__ == "__main__":
    main()
