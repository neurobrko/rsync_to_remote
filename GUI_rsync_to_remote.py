#!/usr/bin/env python3

import PySimpleGUI as sg
from error_handler import WrongConfiguration, NoChangeToConfig
import re
from os import path, chdir
from subprocess import run
import yaml


# define paths
script_root = path.dirname(path.realpath(__file__))
conf_file = path.join(script_root, "sync_conf.yaml")
rsync_file = path.join(script_root, "rsync_to_remote.py")
filemap_file = path.join(script_root, "file_map.yaml")
icon_file = path.join(script_root, "icons/settings.png")

# import configuration variables
with open(conf_file, "r") as f:
    config = yaml.safe_load(f)

# load variables
# create empty variables just for pyCharm not to raise undefined variable warning.
host = username = port = local_root_dir = rsync_options = ""
VM_check_timeout = result_timeout = default_dir = date_format = ""
project = file_keys = ""
sync_all = False
GN = GB = RN = RB = CN = CB = WU = BLD = UND = RST = ""
sg_theme = DEFTC = CHANGETC = ERRTC = ""
for vals in config.values():
    vars().update(vals)

# load file pair map
with open(filemap_file, "r") as f:
    file_map = yaml.safe_load(f)


def get_map_keys(filemap):
    map_keys = []
    for mapa in filemap.values():
        map_keys += [k for k in mapa.keys()]
    return map_keys


def validate_changes(vals, window):
    # TODO: invalid changes just print error in window, not raise error and break
    """Get changed values and validate them"""
    changed_values = {}

    if vals["-HOST-"] != host:
        if vals["-HOST-"] != "localhost":
            if len(host_ip := vals["-HOST-"].split(".")) != 4:
                window["-ERROR-FIELD-"].update("Invalid host!")
            try:
                [int(add) for add in host_ip]
            except:
                window["-ERROR-FIELD-"].update("Invalid host!")

        changed_values["host = "] = [
            f"host = \"{vals['-HOST-']}\"",
            "-r",
            vals["-HOST-"],
        ]
    if vals["-USERNAME-"] != username:
        pattern = re.compile(r"[a-zA-Z0-9]+")
        if not re.fullmatch(pattern, vals["-USERNAME-"]):
            raise WrongConfiguration("Invalid username!")

        changed_values["username = "] = [
            f"username = \"{vals['-USERNAME-']}\"",
            "-u",
            vals["-USERNAME-"],
        ]
    if vals["-PORT-"] != port:
        try:
            int(vals["-PORT-"])
        except:
            raise WrongConfiguration("Invalid port!")
        changed_values["port ="] = [
            f"port = \"{vals['-PORT-']}\"",
            "-s",
            vals["-PORT-"],
        ]
    # specifying -e option is kind of a brute force, but working for this case
    global rsync_options
    if vals["-RSYNC-OPT-"] != " ".join(rsync_options):
        try:
            options = vals["-RSYNC-OPT-"].split()
            e_index = options.index("-e")
            del options[e_index : e_index + 4]
            rsync_options = "["
            for opt in options:
                rsync_options = rsync_options + f'"{opt}", '
            rsync_options = rsync_options + '"-e", f"ssh -p {port}"]'

        except:
            raise WrongConfiguration("Invalid rsync arguments!")
        changed_values["rsync_options ="] = [
            f"rsync_options = {rsync_options}",
        ]
    if vals["-LRD-"] != local_root_dir:
        if path.exists(vals["-LRD-"]) or vals["-LRD-"] == "":
            changed_values["local_root_dir ="] = [
                f"local_root_dir = \"{vals['-LRD-']}\"",
                "-l",
                vals["-LRD-"],
            ]
        else:
            raise WrongConfiguration("Invalid path to local root directory!")
    if int(vals["-VCT-"]) != VM_check_timeout:
        try:
            int(vals["-VCT-"])
        except:
            raise WrongConfiguration("Invalid VM check timeout!")
        changed_values["VM_check_timeout ="] = [
            f"VM_check_timeout = {vals['-VCT-']}",
            "-vt",
            vals["-VCT-"],
        ]
    if int(vals["-RCT-"]) != result_timeout:
        try:
            int(vals["-RCT-"])
        except:
            raise WrongConfiguration("Invalid Result check timeout!")
        changed_values["result_timeout ="] = [
            f"result_timeout = {vals['-RCT-']}",
            "-rt",
            vals["-RCT-"],
        ]
    if vals["-DTF-"] != date_format:
        # probably too complex for validation for sake of this script
        changed_values["date_format ="] = [f"date_format = \"{vals['-DTF-']}\""]

    if vals["-SYNC-ALL-"] != sync_all:
        if type(vals["-SYNC-ALL-"]) != bool:
            raise WrongConfiguration("Something went horribly wrong with checkbox!")
        changed_values["sync_all ="] = [
            f"sync_all = {vals['-SYNC-ALL-']}",
            "-l",
            vals["-SYNC-ALL-"],
        ]
    if vals["-PROJECT-"] == "---":
        option = None
    else:
        option = vals["-PROJECT-"]

    if option != project:
        if not option:
            changed_values["project ="] = [
                f"project = None",
                "",
                "",
            ]
        else:
            changed_values["project ="] = [
                f'project = "{option}"',
                "-p",
                vals["-PROJECT-"],
            ]
    err = ""
    try:
        map_keys = get_map_keys(file_map)
        if (new_keys := [int(key) for key in vals["-KEYS-"].split()]) != file_keys:
            for key in new_keys:
                if key not in map_keys:
                    err = "Supplied key not in file map!"
                    raise WrongConfiguration(err)
            changed_values["file_keys ="] = [
                f"file_keys = {new_keys}",
                "-f",
                ",".join([str(key) for key in new_keys]),
            ]

    except:
        if not err:
            err = "Invalid file keys!"
        raise WrongConfiguration(err)
    return changed_values


def update_conf(values, window):
    """Update configuration file with changed values"""
    changes = validate_changes(values, window)
    if len(changes) == 0:
        raise NoChangeToConfig("There were no changes in configuration!")
    with open(conf_file, "r") as file:
        lines = file.readlines()

    for change, values in changes.items():
        for i, line in enumerate(lines):
            if change in line and "#" not in line:
                lines[i] = f"{values[0]}\n"

    with open(conf_file, "w") as file:
        file.writelines(lines)
    return changes


def get_cmd_list(values, window):
    """
    Return list od arguments for subprocess.run()
    to run rsync_to_remote.py with modified arguments
    """
    changes = validate_changes(values, window)
    cmd_list = [
        "/home/marpauli/.cache/pypoetry/virtualenvs/rsync-to-vm-yQGWRMhR-py3.12/bin/python",
        rsync_file,
    ]
    for k, vals in changes.items():
        if k == "rsync_options =":
            continue
        cmd_list = cmd_list + vals[1:3]

    return cmd_list


# set theme for GUI
sg.theme(sg_theme)


# most used line generator
def config_line(name, value, key, width=80):
    """Generator for most used line in GUI"""
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


# set variables and fields dict for colorizing changed output
DEFTC = "lightgrey"
CHANGETC = "red"
ERRTC = "yellow"

if not project:
    opt_def_val = "---"
else:
    opt_def_val = project

fields = {
    "-HOST-": host,
    "-USERNAME-": username,
    "-PORT-": port,
    "-RSYNC-OPT-": rsync_options,
    "-LRD-": local_root_dir,
    "-VCT-": VM_check_timeout,
    "-RCT-": result_timeout,
    "-DTF-": date_format,
    "-SYNC-ALL-": sync_all,
    "-PROJECT-": opt_def_val,
    "-KEYS-": file_keys,
}


# configure layout
layout = [
    [
        sg.Column(config_line("remote host:", host, "-HOST-", 29)),
        sg.Column(config_line("username:", username, "-USERNAME-", 29)),
        sg.Column(config_line("port:", port, "-PORT-", 15)),
    ],
    [sg.Column(config_line("rsync options:", " ".join(rsync_options), "-RSYNC-OPT-"))],
    [
        sg.Column(
            [
                [
                    sg.Text(
                        "WARNING! rsync options are ignored when running w/o update conf! (TODO)",
                        text_color="yellow",
                    )
                ]
            ]
        )
    ],
    [
        sg.Column(
            [
                [sg.Text("local root dir:")],
                [
                    sg.InputText(
                        size=(68, 1),
                        key="-LRD-",
                        default_text=local_root_dir,
                        enable_events=True,
                        text_color=DEFTC,
                    ),
                    sg.Push(),
                    sg.FolderBrowse(target="-LRD-"),
                ],
            ]
        )
    ],
    [
        sg.Column(config_line("VM check timeout:", VM_check_timeout, "-VCT-", 20)),
        sg.Column(config_line("Result check timeout:", result_timeout, "-RCT-", 20)),
        sg.Column(config_line("datetime format:", date_format, "-DTF-", 33)),
    ],
    [
        sg.Column(
            [
                [
                    sg.Checkbox(
                        " Synchronize all ",
                        default=sync_all,
                        key="-SYNC-ALL-",
                        enable_events=True,
                    ),
                    sg.Text("Synchronize project:"),
                    sg.Combo(
                        ["---"] + list(file_map.keys()),
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
                " ".join([str(key) for key in file_keys]),
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
    [sg.HSeparator(pad=((10, 10), (10, 10)), color="black")],
    [sg.Text("", text_color=ERRTC, key="-ERROR-FIELD-")],
]


def main():
    # change dir for FileBrowse()
    if path.exists(default_dir):
        chdir(default_dir)
    elif path.exists(local_root_dir):
        chdir(local_root_dir)
    # Create window
    window = sg.Window("Configure rsync_to_remote.py", layout, icon=icon_file)
    # Create an event loop
    while True:
        event, values = window.read()
        # End program if user clicks on OK, or closes the window
        if event in ("Exit", sg.WIN_CLOSED):
            break
        elif event == "Run":
            # run the command with cli arguments based on changes
            cmd_list = get_cmd_list(values, window)
            # run(cmd_list)
            # break
        elif event == "Update conf":
            # update sync_conf, but do not run
            update_conf(values, window)
            print(f"\033[1;32mConfiguration successfully updated!\033[0m")
            break
        elif event == "Update conf & Run":
            # update sync_conf
            update_conf(values, window)
            # run using new settings
            run(
                [
                    "/home/marpauli/.cache/pypoetry/virtualenvs/rsync-to-vm-yQGWRMhR-py3.12/bin/python",
                    rsync_file,
                ]
                # production python bin: /home/marpauli/code/cisco/rsync_to_VM/production/.venv/bin/python3.12
            )
            break
        elif event in list(fields.keys()):
            if fields[event] != values[event]:
                if event == "-RSYNC-OPT-":
                    if " ".join(rsync_options) != values[event]:
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
                    if " ".join([str(key) for key in file_keys]) != values[event]:
                        window[event].update(text_color=CHANGETC)
                    else:
                        window[event].update(text_color=DEFTC)
                else:
                    window[event].update(text_color=CHANGETC)
            else:
                window[event].update(text_color=DEFTC)

    window.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\033[1;31m{type(e).__name__}:\033[0m {e}")
