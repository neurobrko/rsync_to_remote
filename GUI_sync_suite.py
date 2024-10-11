#!/usr/bin/env python3

# python env for production:
# /home/marpauli/code/cisco/rsync_to_VM/production/.venv/bin/python3.12

import PySimpleGUI as sg
from os import path
from subprocess import run
from GUI_rsync_to_remote import get_center, read_yaml

script_root = path.dirname(path.realpath(__file__))
conf_file = path.join(script_root, "sync_conf.yaml")
conf = read_yaml(conf_file)
text_editor = "/usr/bin/gedit"
sg.theme(conf["gui"]["sg_theme"])
FONT = "Ubuntu"

layout = [
    [
        sg.Text(
            "Sync Suite",
            font=(FONT, 36, "bold"),
            text_color="grey24",
            pad=((0, 0), (0, 10)),
        )
    ],
    [
        sg.Column(
            [
                [
                    sg.Image(
                        filename="sync_suite/sync.png",
                        enable_events=True,
                        key="-SYNC-",
                    ),
                ],
                [
                    sg.Text(
                        "Instant sync",
                        pad=((0, 0), (5, 25)),
                        font=(FONT, 12, "bold"),
                        enable_events=True,
                        key="-T-SYNC-",
                    )
                ],
                [
                    sg.Image(
                        filename="sync_suite/map.png",
                        enable_events=True,
                        key="-MAP-",
                    ),
                ],
                [
                    sg.Text(
                        "Show file map",
                        pad=((0, 0), (5, 25)),
                        font=(FONT, 12, "bold"),
                        enable_events=True,
                        key="-T-MAP-",
                    )
                ],
            ],
            element_justification="center",
            pad=((50, 25), (0, 0)),
        ),
        sg.Column(
            [
                [
                    sg.Image(
                        filename="sync_suite/settings.png",
                        enable_events=True,
                        key="-SETT-",
                    ),
                ],
                [
                    sg.Text(
                        "Sync options",
                        pad=((0, 0), (5, 25)),
                        font=(FONT, 12, "bold"),
                        enable_events=True,
                        key="-T-SETT-",
                    )
                ],
                [
                    sg.Image(
                        filename="sync_suite/config.png",
                        enable_events=True,
                        key="-CONF-",
                    ),
                ],
                [
                    sg.Text(
                        "Show config",
                        pad=((0, 0), (5, 25)),
                        font=(FONT, 12, "bold"),
                        enable_events=True,
                        key="-T-CONF-",
                    )
                ],
            ],
            element_justification="center",
            pad=((50, 25), (0, 0)),
        ),
        sg.Column(
            [
                [
                    sg.Image(
                        filename="sync_suite/add.png",
                        enable_events=True,
                        key="-ADD-",
                    ),
                ],
                [
                    sg.Text(
                        "Add files to sync",
                        pad=((0, 0), (5, 25)),
                        font=(FONT, 12, "bold"),
                        enable_events=True,
                        key="-T-ADD-",
                    )
                ],
                [
                    sg.Image(
                        filename="sync_suite/log.png",
                        enable_events=True,
                        key="-LOG-",
                    ),
                ],
                [
                    sg.Text(
                        "Show last log",
                        pad=((0, 0), (5, 25)),
                        font=(FONT, 12, "bold"),
                        enable_events=True,
                        key="-T-LOG-",
                    )
                ],
            ],
            element_justification="center",
            pad=((50, 25), (0, 0)),
        ),
    ],
]


window = sg.Window(
    "Run and manage your synchronization",
    layout,
    finalize=True,
    icon="icons/rsync.png",
    grab_anywhere=True,
)
window.move((pos := get_center(window))[0], pos[1])

while True:
    event, values = window.read()
    print(event)
    if event in ("-SYNC-", "-T-SYNC-"):
        run(path.join(script_root, "rsync_to_remote.py"))
    if event in ("-SETT-", "-T-SETT-"):
        run(path.join(script_root, "GUI_rsync_to_remote.py"))
    if event in ("-ADD-", "-T-ADD-"):
        run(path.join(script_root, "GUI_add_map.py"))
    if event in ("-MAP-", "-T-MAP-"):
        run([text_editor, path.join(script_root, "file_map.yaml")])
    if event in ("-CONF-", "-T-CONF-"):
        run([text_editor, path.join(script_root, "sync_conf.yaml")])
    if event in ("-LOG-", "-T-LOG-"):
        run(path.join(script_root, "GUI_show_log.py"))
    if event == sg.WIN_CLOSED:
        break

window.close()
