#!/usr/bin/env python3

# python env for production:
# /home/marpauli/code/cisco/rsync_to_VM/production/.venv/bin/python3.12

import PySimpleGUI as sg
import re
from os import path, chdir, stat, listdir, remove
from subprocess import run
from datetime import datetime
from time import time, sleep
import yaml
import screeninfo
from platform import system

# testing
python_env = (
    "/home/marpauli/.cache/pypoetry/virtualenvs/rsync-to-vm-yQGWRMhR-py3.12/bin/python"
)
# production
# python_env = "/home/marpauli/code/cisco/rsync_to_VM/production/.venv/bin/python3.12"

# define paths
script_root = path.dirname(path.realpath(__file__))
conf_file = path.join(script_root, "sync_conf.yaml")
rsync_file = path.join(script_root, "rsync_to_remote.py")
filemap_file = path.join(script_root, "file_map.yaml")
icon_file = path.join(script_root, "icons/settings.png")
log_dir = path.join(script_root, "log")


def read_yaml(file):
    with open(file, "r") as f:
        content = yaml.safe_load(f)
    return content


# if log_dir existst delete log older than 3 days (72 hours to be exact)
if path.exists(log_dir):
    [
        remove(del_logfile)
        for logfile in listdir(log_dir)
        if stat((del_logfile := path.join(log_dir, logfile))).st_mtime
        < time() - 3 * 86400
    ]


# import configuration variables
config = read_yaml(conf_file)
# load variables
# create empty variables just for pyCharm not to raise undefined variable warning.
host = username = port = local_root_dir = rsync_options = ""
VM_check_timeout = result_timeout = default_browse_dir = date_format = ""
project = file_keys = ""
sync_all = False
GN = GB = RN = RB = CN = CB = WU = BLD = UND = RST = ""
sg_theme = DEFTC = CHANGETC = ERRTC = text_editor = terminal_app = ""
for vals in config.values():
    vars().update(vals)

# get system info and set command for running in console
system = system().lower()
terminal_run = [
    terminal_app,
    "--",
    "bash",
    "-c",
]

# load file pair map
file_map = read_yaml(filemap_file)


def get_center(win) -> tuple[int, int]:
    m_size = ""
    for _ in screeninfo.get_monitors():
        if _.is_primary:
            m_size = _
    w_size = win.size
    x = int(m_size.x + m_size.width / 2 - w_size[0] / 2)
    y = int(m_size.y + m_size.height / 2 - w_size[1] / 2)

    return x, y


def get_map_keys(filemap):
    map_keys = []
    for mapa in filemap.values():
        map_keys += [k for k in mapa.keys()]
    return map_keys


def validate_changes(vals, window):
    """Get changed values and validate them"""
    changed_values = {}
    is_valid = True

    if vals["-HOST-"] != host:
        if vals["-HOST-"] != "localhost":
            if len(host_ip := vals["-HOST-"].split(".")) != 4:
                window["-ERROR-FIELD-"].update("Invalid host!")
                is_valid = False
            else:
                try:
                    [int(add) for add in host_ip]
                    changed_values["host"] = [
                        "rsync",
                        vals["-HOST-"],
                        "-r",
                        vals["-HOST-"],
                    ]
                except:
                    window["-ERROR-FIELD-"].update("Invalid host!")
                    is_valid = False
        else:
            changed_values["host"] = [
                "rsync",
                vals["-HOST-"],
                "-r",
                vals["-HOST-"],
            ]

    if vals["-USERNAME-"] != username:
        pattern = re.compile(r"[a-zA-Z0-9]+")
        if not re.fullmatch(pattern, vals["-USERNAME-"]):
            window["-ERROR-FIELD-"].update("Invalid username!")
            is_valid = False
        else:
            changed_values["username"] = [
                "rsync",
                vals["-USERNAME-"],
                "-u",
                vals["-USERNAME-"],
            ]
    if vals["-PORT-"] != str(port):
        try:
            int(vals["-PORT-"])
            changed_values["port"] = [
                "rsync",
                int(vals["-PORT-"]),
                "-s",
                vals["-PORT-"],
            ]
        except:
            window["-ERROR-FIELD-"].update("Invalid port number!")
            is_valid = False

    # specifying -e option is kind of a brute force, but working for this case
    global rsync_options
    if vals["-RSYNC-OPT-"] != " ".join(rsync_options) or vals["-PORT-"] != str(port):
        try:
            options = vals["-RSYNC-OPT-"].split()
            e_index = options.index("-e")
            del options[e_index : e_index + 4]
            rsync_options = options + ["-e", f"ssh -p {vals['-PORT-']}"]
            changed_values["rsync_options"] = [
                "rsync",
                rsync_options,
                "",
                "",
            ]
        except:
            window["-ERROR-FIELD-"].update("Invalid rsync arguments!")
            is_valid = False

    if vals["-LRD-"] != local_root_dir:
        if path.exists(vals["-LRD-"]) or vals["-LRD-"] == "":
            if vals["-LRD-"] == "":
                val_to_cmd = " "
            else:
                val_to_cmd = vals["-LRD-"]
            changed_values["local_root_dir"] = [
                "rsync",
                vals["-LRD-"],
                "-l",
                val_to_cmd,
            ]
        else:
            window["-ERROR-FIELD-"].update("Invalid path to local root directory!")
            is_valid = False
    if vals["-VCT-"] != str(VM_check_timeout):
        try:
            int(vals["-VCT-"])
            changed_values["VM_check_timeout"] = [
                "script",
                int(vals["-VCT-"]),
                "-vt",
                vals["-VCT-"],
            ]
        except:
            window["-ERROR-FIELD-"].update("Invalid VM check timeout!")
            is_valid = False

    if vals["-RCT-"] != str(result_timeout):
        try:
            int(vals["-RCT-"])
            changed_values["result_timeout"] = [
                "script",
                int(vals["-RCT-"]),
                "-rt",
                vals["-RCT-"],
            ]
        except:
            window["-ERROR-FIELD-"].update("Invalid Result check timeout!")
            is_valid = False

    if vals["-DTF-"] != date_format:
        # validation Mark I Eyeball at GUI
        changed_values["date_format"] = ["script", vals["-DTF-"], "-d", vals["-DTF-"]]

    if vals["-SYNC-ALL-"] != sync_all:
        if type(vals["-SYNC-ALL-"]) != bool:
            window["-ERROR-FIELD-"].update(
                "Something went horribly wrong with checkbox!"
            )
            is_valid = False
        else:
            changed_values["sync_all"] = [
                "sync",
                vals["-SYNC-ALL-"],
                "-a",
                "",
            ]
    if vals["-PROJECT-"] == "---":
        project_option = None
    else:
        project_option = vals["-PROJECT-"]

    if project_option != project:
        if not project_option:
            changed_values["project"] = ["sync", None, "", ""]
        else:
            changed_values["project"] = [
                "sync",
                project_option,
                "-p",
                project_option,
            ]
    try:
        map_keys = get_map_keys(file_map)
        if vals["-KEYS-"] == "" and (
            vals["-PROJECT-"] == "---" and vals["-SYNC-ALL-"] == False
        ):
            window["-ERROR-FIELD-"].update(
                "This setting would yield nothing to synchronize!"
            )
            is_valid = False
        elif (new_keys := [int(key) for key in vals["-KEYS-"].split()]) != file_keys:
            for key in new_keys:
                if key not in map_keys:
                    window["-ERROR-FIELD-"].update("Supplied key not in file map!")
                    is_valid = False
                    # continue
                else:
                    changed_values["file_keys"] = [
                        "sync",
                        new_keys,
                        "-f",
                        ",".join([str(key) for key in new_keys]),
                    ]

    except:
        window["-ERROR-FIELD-"].update("Invalid file keys!")
        is_valid = False

    return changed_values or None, is_valid


def update_conf(values, window):
    """Update configuration file with changed values"""
    changes, is_valid = validate_changes(values, window)
    if is_valid:
        if not changes:
            window["-ERROR-FIELD-"].update("There were no changes in configuration!")
        else:
            for change, ch_list in changes.items():
                config[ch_list[0]][change] = ch_list[1]
            with open(conf_file, "w") as file:
                yaml.dump(config, file, sort_keys=False)
        return changes


def get_cmd_list(values, window):
    """
    Return list of arguments for subprocess.run()
    to run rsync_to_remote.py with modified arguments
    """
    changes, is_valid = validate_changes(values, window)
    if is_valid:
        cmd_list = [
            python_env,
            rsync_file,
        ]
        if changes:
            for k, vals in changes.items():
                if k == "rsync_options":
                    continue
                for val in vals[-2:]:
                    val and cmd_list.append(val)
        return cmd_list
    else:
        return None


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
                        "WARNING! rsync options are ignored when running w/o update conf!",
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
        ),
        sg.Push(),
        sg.Column(
            [
                [
                    sg.Text(
                        f"(example: {datetime(2000, 12, 24, 12, 53, 7).strftime(date_format)})",
                        text_color="gray",
                        key="-DTEX-",
                        justification="right",
                    )
                ]
            ]
        ),
    ],
    [
        sg.Column(
            [
                [sg.Text("file pair keys (space separated):")],
                [
                    sg.InputText(
                        size=(67, 1),
                        key="-KEYS-",
                        default_text=" ".join([str(key) for key in file_keys]),
                        enable_events=True,
                        text_color=DEFTC,
                    ),
                    sg.Push(),
                    sg.Button("Get keys", key="-GET-KEYS-"),
                ],
            ]
        )
    ],
    [
        sg.Column(
            [
                [
                    sg.Button("Run"),
                    sg.Button("Update conf"),
                    sg.Button("Update conf & Run"),
                    sg.VerticalSeparator(),
                    sg.Button("File map cleanup", key="-DEL-KEYS-"),
                    sg.VerticalSeparator(),
                ]
            ]
        ),
        sg.Push(),
        sg.Column([[sg.Button("Exit")]]),
    ],
    [sg.HSeparator(pad=((10, 10), (10, 10)), color="black")],
    [sg.Text("", text_color=ERRTC, key="-ERROR-FIELD-")],
]


def new_window_get_keys(parent_window):
    layout_pop = [
        [sg.Text("Select file pair keys:", size=(40, 1))],
        [
            (
                [sg.Text(f"{proj}:")],
                [
                    (
                        [
                            sg.Checkbox(
                                f" [{key}]: {path.basename(mapa[0])}",
                                default=True if key in file_keys else False,
                                key=int(key),
                                pad=((10, 0), (0, 0)),
                                tooltip=f"src: {mapa[0]}\ntrg: {mapa[1]}",
                            )
                        ],
                    )
                    for key, mapa in maps.items()
                ],
            )
            for proj, maps in file_map.items()
        ],
        [sg.Button("Insert"), sg.Push(), sg.Button("Close")],
    ]

    window_pop = sg.Window(
        "Select files to sync",
        layout_pop,
        icon=icon_file,
        finalize=True,
        grab_anywhere=True,
    )
    window_pop.move((pos := get_center(window_pop))[0], pos[1])

    while True:
        event_pop, values_pop = window_pop.read()
        if event_pop in ("Close", sg.WIN_CLOSED):
            break
        if event_pop == "Insert":
            insert_keys = []
            for key, value in values_pop.items():
                value and insert_keys.append(str(key))
            parent_window["-KEYS-"].update(" ".join(insert_keys))
            break
    window_pop.close()


def file_map_cleanup():
    pad = ((25, 0), (0, 0))
    layout_del = [
        [sg.Text("Select file pair keys:", size=(40, 1))],
        [
            (
                [sg.Checkbox(f" {proj}", key=proj)],
                [
                    (
                        [
                            sg.Checkbox(
                                f" [{key}]: {path.basename(mapa[0])}",
                                key=int(key),
                                pad=pad,
                                tooltip=f"src: {mapa[0]}\n trg: {mapa[1]}",
                            )
                        ],
                    )
                    for key, mapa in maps.items()
                ],
            )
            for proj, maps in file_map.items()
        ],
        [sg.Button("Delete!", button_color="red"), sg.Push(), sg.Button("Close")],
    ]

    window_del = sg.Window(
        "Delete files from file_map.yaml",
        layout_del,
        icon=icon_file,
        finalize=True,
        grab_anywhere=True,
    )
    window_del.move((pos := get_center(window_del))[0], pos[1])

    while True:
        event_del, values_del = window_del.read()
        if event_del in ("Close", sg.WIN_CLOSED):
            break
        if event_del == "Delete!":
            # get all the checkbox keys
            keys = [key for key, val in values_del.items() if val]
            # filter out projects to delete completely
            projects_to_del = [key for key in keys if type(key) == str]
            # get keys of deleted projects
            project_keys = []
            for k, v in file_map.items():
                if k in projects_to_del:
                    project_keys += [k for k in v.keys()]
            # filter out keys to delete from projects that are not deleted completely
            keys_to_del = [
                key for key in keys if type(key) == int and key not in project_keys
            ]
            # delete projects
            for key in projects_to_del:
                del file_map[key]
            # cycle through rest of the project and delete rest of the keys
            for k in keys_to_del:
                for key, mapa in file_map.items():
                    if k in mapa.keys():
                        del file_map[key][k]
            # remove empty projects
            empty_projects = []
            for proj, mapa in file_map.items():
                if not mapa:
                    empty_projects.append(proj)
            for proj in empty_projects:
                del file_map[proj]
            # update file_map.yaml
            with open(filemap_file, "w") as file:
                yaml.dump(file_map, file, sort_keys=False)
            break
    window_del.close()


def main():
    # change dir for FileBrowse()
    if path.exists(default_browse_dir):
        chdir(default_browse_dir)
    elif path.exists(local_root_dir):
        chdir(local_root_dir)
    # Create window
    window = sg.Window(
        "Configure and/or run rsync_to_remote.py", layout, icon=icon_file, finalize=True
    )
    window.move((pos := get_center(window))[0], pos[1])
    # Create an event loop
    while True:
        event, values = window.read()
        # End program if user clicks on OK, or closes the window
        if event in ("Exit", sg.WIN_CLOSED):
            break
        elif event == "Run":
            window["-ERROR-FIELD-"].update("")
            # run the command with cli arguments based on changes
            cmd = get_cmd_list(values, window)
            if cmd:
                if len(cmd) == 2:
                    window["-ERROR-FIELD-"].update(
                        "Running with unchanged configuration..."
                    )
                    window.refresh()
                    sleep(1)
                if "linux" in system:
                    cmd = terminal_run + [" ".join(cmd)]
                    run(cmd)
                else:
                    run(" ".join(cmd))
                break
        elif event == "Update conf":
            # update sync_conf, but do not run
            result = update_conf(values, window)
            if result:
                break
        elif event == "Update conf & Run":
            # update sync_conf
            result = update_conf(values, window)
            # run using new settings
            if result:
                cmd = [rsync_file]
                if "linux" in system:
                    cmd = terminal_run + cmd
                run(cmd)
                break
        elif event == "-GET-KEYS-":
            new_window_get_keys(window)
        elif event == "-DEL-KEYS-":
            file_map_cleanup()
        elif event in list(fields.keys()):
            if event == "-DTF-":
                window["-DTEX-"].update(
                    f"(example: {datetime(2012, 12, 24, 12, 53, 7).strftime(values['-DTF-'])})"
                )
            if fields[event] != values[event]:
                if event == "-RSYNC-OPT-":
                    if " ".join(rsync_options) != values[event]:
                        window[event].update(text_color=CHANGETC)
                    else:
                        window[event].update(text_color=DEFTC)
                elif event in ["-VCT-", "-RCT-"]:
                    if values[event] != "":
                        if str(fields[event]) != values[event]:
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
    main()
    # try:
    #     main()
    # except Exception as e:
    #     print(f"\033[1;31m{type(e).__name__}:\033[0m {e}")
