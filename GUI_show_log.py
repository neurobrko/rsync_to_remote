#!/usr/bin/env python3

# python env for production:
# /home/marpauli/code/cisco/rsync_to_VM/production/.venv/bin/python3.12

import PySimpleGUI as sg
from os import path
from time import strftime, sleep
import yaml
from subprocess import run
from GUI_rsync_to_remote import get_center

script_root = path.dirname(path.realpath(__file__))
conf_file = path.join(script_root, "sync_conf.yaml")
log_filename = f"rsync_to_remote-{strftime('%y%m%d')}.log"
log_file = path.join(script_root, "log", log_filename)
log_viewer = "/usr/bin/gedit"

with open(conf_file, "r") as f:
    conf = yaml.safe_load(f)

sg.theme(conf["gui"]["sg_theme"])
ERRTC = conf["gui"]["ERRTC"]

if not path.exists(log_file):
    layout_warn = [
        [sg.Text("Log file does not exist!", text_color=ERRTC, justification="center")],
        [sg.Push(), sg.Button("Exit"), sg.Push()],
    ]
    window_warn = sg.Window("Error!", layout_warn, location=(1600, 135))
    while True:
        event = window_warn.read()[0]
        if event in ("Exit", sg.WIN_CLOSED):
            break
    window_warn.close()
    exit()

with open(log_file, "r") as f:
    log_content = f.readlines()

last_log = []

for line in log_content[-3::-1]:
    last_log.insert(0, line)
    if "=> SYNC START <=" in line:
        break

layout = [
    [sg.Listbox(values=last_log, size=(100, len(last_log)))],
    [sg.Button("View complete log", key="-VIEW-LOG-"), sg.Push(), sg.Button("Exit")],
]


window = sg.Window("Last log", layout, finalize=True)
window.move((pos := get_center(window))[0], pos[1])
while True:
    event = window.read()[0]
    if event in ("Exit", sg.WIN_CLOSED):
        break
    if event == "-VIEW-LOG-":
        run(
            [log_viewer, log_file],
        )
        break

    window.close()
