#!/usr/bin/env

import sync_conf as sc
from subprocess import run

# OVERRIDE SETTINGS FOR TESTING
sc.host = "localhost"
sc.username = "marpauli"
sc.port = "22"
sc.rsync_options = ["rsync", "-rtvz", "--progress", "-e", f"ssh -p {sc.port}"]
sc.local_root_dir = ""


def get_all_maps(file_map: dict) -> dict:
    all_maps = {}
    for maps in file_map.values():
        new_maps = {k: v for k, v in maps.items()}
        all_maps.update(new_maps)
    return all_maps


def get_project_maps(file_map: dict, project: str) -> dict:
    return file_map[project]


def run_cmd(cmd_list: list):
    run(cmd_list, shell=False, executable="/bin/bash")


file_maps = get_project_maps(sc.file_map, "test")

cmd_list = sc.rsync_options
for paths in file_maps.values():
    run_cmd(
        [
            "rsync",
            "-rtvz",
            "--progress",
            "-e",
            f"'ssh -p {sc.port}'",
            paths[0],
            f"{sc.username}@{sc.host}:{paths[2]}",
        ]
    )

run_cmd(cmd_list)
