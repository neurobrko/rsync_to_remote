#!/usr/bin/env python

from sync_conf import file_map, host, username, port
from GUI_rsync_to_VM import get_map_keys
from subprocess import run, PIPE
from os import path

map_keys = get_map_keys(file_map)

# file = "drivers/runtime/systemd-services/virl2-initial-setup.py"
file = "core/simple_core/controller/events.py"
basename = path.basename(file)


def get_remote_target():
    """Get path to remote target based on local name."""
    remote_files = (
        run(
            [
                "ssh",
                "-p",
                f"{port}",
                f"{username}@{host}",
                "find",
                "/",
                "-name",
                f"{basename}",
            ],
            text=True,
            stdout=PIPE,
        )
        .stdout.strip()
        .split("\n")
    )
    return remote_files


def find_next_key(keys: list):
    """Find next free key for file map dictionary."""
    for i in range(1, len(keys) + 2):
        if i not in keys:
            return i
