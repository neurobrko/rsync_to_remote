#!/usr/bin/env python

import PySimpleGUI as sg
import sync_conf as sc
from time import sleep

# THIS WILL BE GUI FOR CONFIGURING BEHAVIOUR OF rsync_to_VM.py
# EITHER ONE-TIME BY RUNNING IT WITH CLI ARGUMENTS
# OR PERMANENTLY (UNTIL NEXT CONFIG) BY CHANGING sync_conf.py

sg.theme("DarkGrey11")
DEFTC = "lightgrey"
CHANGETC = "red"


def config_line(name, value, key, width=80):
    return [
        [sg.Text(f"{name}")],
        [
            sg.InputText(
                size=(width, 1),
                key=key,
                default_text=value,
                enable_events=True,
                text_color=DEFTC,
            )
        ],
    ]


if not sc.project:
    opt_def_val = "---"
else:
    opt_def_val = sc.project

fields = {
    "-HOST-": sc.host,
    "-USERNAME-": sc.username,
    "-HOST-ADDRESS-": sc.host_address,
    "-PORT-": sc.port,
    "-RSYNC-OPT-": sc.rsync_options,
    "-LRD-": sc.local_root_dir,
    "-VCT-": sc.VM_check_timeout,
    "-RCT-": sc.result_timeout,
    "-DTF-": sc.date_format,
    "-SYNC-ALL-": sc.sync_all,
    "-PROJECT-": opt_def_val,
    "-KEYS-": sc.file_keys,
}


# configure layout
layout = [
    [sg.Column(config_line("Connect to host:", sc.host, "-HOST-"))],
    [
        sg.Column(config_line("username:", sc.username, "-USERNAME-", 33)),
        sg.Column(
            config_line("VM host address:", sc.host_address, "-HOST-ADDRESS-", 20)
        ),
        sg.Column(config_line("port:", sc.port, "-PORT-", 20)),
    ],
    [
        sg.Column(
            config_line("rsync options:", " ".join(sc.rsync_options), "-RSYNC-OPT-")
        )
    ],
    [sg.Column(config_line("local root dir:", sc.local_root_dir, "-LRD-"))],
    [
        sg.Column(config_line("VM check timeout:", sc.VM_check_timeout, "-VCT-", 20)),
        sg.Column(config_line("Result check timeout:", sc.result_timeout, "-RCT-", 20)),
        sg.Column(config_line("datetime format:", sc.date_format, "-DTF-", 33)),
    ],
    [
        sg.Column(
            [
                [
                    sg.Checkbox(
                        " Synchronize all ",
                        default=sc.sync_all,
                        key="-SYNC-ALL-",
                        enable_events=True,
                    ),
                    sg.Text("Synchronize project:"),
                    sg.Combo(
                        ["---"] + list(sc.file_map.keys()),
                        default_value=opt_def_val,
                        key="-PROJECT-",
                        enable_events=True,
                    ),
                ]
            ]
        )
    ],
    [
        sg.Column(
            config_line(
                "file pair keys (space separated):",
                " ".join([str(key) for key in sc.file_keys]),
                "-KEYS-",
            )
        )
    ],
    [
        sg.Column(
            [
                [
                    sg.Button("Run"),
                    sg.Button("Update conf"),
                    sg.Button("Update conf & Run"),
                ]
            ]
        ),
        sg.Push(),
        sg.Column([[sg.Button("Exit")]]),
    ],
]

# Create window
window = sg.Window("Configure rsync_to_VM.py", layout)
# Create an event loop
while True:
    event, values = window.read()
    # End program if user clicks on OK, or closes the window
    if event in ("Exit", sg.WIN_CLOSED):
        break
    elif event == "Run":
        print("Run")
        break
    elif event == "Update conf":
        print("Update")
        break
    elif event == "Update conf & Run":
        print("Update & Run")
        break
    elif event in list(fields.keys()):
        if fields[event] != values[event]:
            if event == "-RSYNC-OPT-":
                if " ".join(sc.rsync_options) != values[event]:
                    window[event].update(text_color=CHANGETC)
                else:
                    window[event].update(text_color=DEFTC)
            elif event in ["-VCT-", "-RCT-"]:
                if values[event] != "":
                    if fields[event] != int(values[event]):
                        window[event].update(text_color=CHANGETC)
                    else:
                        window[event].update(text_color=DEFTC)
            elif event == "-KEYS-":
                if " ".join([str(key) for key in sc.file_keys]) != values[event]:
                    window[event].update(text_color=CHANGETC)
                else:
                    window[event].update(text_color=DEFTC)
            else:
                window[event].update(text_color=CHANGETC)
        else:
            window[event].update(text_color=DEFTC)

window.close()
print(values)
