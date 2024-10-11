# Synchronize files to remote
author: elvis (Marek Paulik)\
mail: elvis@elvis.sk

**Set of tools to manage and perform synchronization of files to remote system using rsync. Script also ouptuts 
its action to console and logs them.**

**IMPORTANT:** 
See section _Installation and usage_ for minimum mandatory steps to get scripts working properly.

_**GUI_sync_suite.py**_ - wrapper script to get all the functionality in one place (SySu)

_**rsync_to_remote.py**_ - standalone CLI script to perform synchronization. Configuration is loaded from _sync_conf.yaml_, 
but can be altered using CLI arguments. See _rsync_to_remote.py -h_.

_**GUI_rsync_to_remote.py**_ - GUI tool for changing configuration saved in _sync_conf.py_. It also allows you to either 
run sync dw/o changing configuration, or alter configuration (one-time or permanently) or just save new configuration.

_**GUI_add_map.py**_ - synchronization uses list of file pairs stored in _file_map.yaml_ passed to rsync. Each pair is
subset of project. It gives you opportunity to sync all files in project, or just selected files throughout all projects.

_**GUI_show_log.py**_ - show log for last sync. Option to view complete log file.

## Instalation and usage ##
Use Poetry or venv or install requirements directly onto your system (not recommended).

**IMPORTANT:** 
- Change variable _python_env_ in GUI_rsync_to_remote.py[line:16] to match your interpreter.
- Change _text_editor_ value in _gui_ section in sync_conf.yaml to match your system text editor

_Tip for pyCharm:_ put path to your Poetry/venv interpreter directly to shabang, so you can run scripts using External Tools
and add them to any panel.

**For possible use scenario see end of this document.**

### _sync_conf.yaml_
File contains configuration used for running _rsync_to_remote.py_ and some settings for GUI. Most of the settings can
be changed using _GUI_rsync_to_remote.py_. If you decide to change them by hand, there are few rules to follow.

**format:** {category: {var1: val1, var2: val2}}

- ALWAYS make backup before editing by hand!

**RSYNC SETTINGS**
  - when editing port, always edit rsync option accordingly!
  - local_root_dir should ALWAYS contain valid path, BUT if empty, must be "" (same goes for default_dir)

**SCRIPT SETTINGS**
  - set timeout to 0 to skip check
  - set default_dir to specify dir to start browsing from local_root_dir (LRD) is used if empty, if LRD empty 
script parent dir is used

**SYNC SETTINGS**\
  INFO: Override hierarchy: _**sync_all**_ > _**project**_ <project> > _**file_keys**_
  - sync_all: sync all files in _file_map.yaml_; value: true/false
  - project: sync all files from specified project, null for None
  - file_keys: list of file pairs to sync
    WARNING: Must be list even with zero or single item! hint: empty_list: []

**COLORS SETTINGS**\
   GN: green normal\
   GB: green bold\
   RN: red normal\
   RB: red bold\
   CN: cyan normal\
   CB: cyan bold\
   WU: white underline\
   BLD: bold\
   UND: underline\
   RST: reset formatting

### _file_map.yaml_
**format:** {project: [source/path, target/path]}

### Possible installation scenario ###
- clone repo, create venv, install requirements
```
> mkdir /your/repo/dir
> cd /your/repo/dir
> git clone https://github.com/neurobrko/rsync_to_remote.git .
> python3 -m venv .venv
> source .venv/bin/python3
(.venv) > pip install -r requirements.txt
(.venv) > deactivate
```
- edit files and sync_conf.yaml
  - change "shabang" in: (1) _GUI_add_map.py_, (2) _GUI_rsync_to_remote.py_, (3) _GUI_show_log.py_, (4) _rsync_to_remote.py_ to:\
  `#!/your/repo/dir/.venv/bin/python3`
  - in _GUI_rsync_to_remote.py_ change value of variable _python_env_ to:\
  `"/your/repo/dir/.venv/bin/python3"`
  - in _sync_conf.yaml_ change value of _text_editor_ in _gui_ section to your favourite yaml viewer. (In Win, Notepad should be OK.)
  - create launcher/desktop shortcut/taskbar pin for command:\
  `/your/repo/dir/.venv/bin/python3 /your/repo/dir/GUI_sync_suite.py`\
    (To be honest, I have no idea how that's done on Windows.)
  - Launch Sync Suite (SySU)
  - hit 'Sync options' in SySu
  - edit _local root dir_ to match your location of files you want to sync, then press _\<Update conf\>_
     - you can also edit remote settings (_hostname_, _username_, _port_ and _rsync options_) 
  - hit 'Add files to sync' in SySu
  - _\<Browse\>_ to your source file or write it in directly
  - if you set remote settings in previous step, you can use _\<Get target\>_ to obtain your target file, or write it in\
    (It must be full path!)
  - input name of your project and press _\<Add to project\>_
  - hit 'Show file map' in SySu and remove all lines preceding your new project
  - hit 'Instant sync' in SySU and enjoy! :)
  - You can also add launchers for the scripts to your IDE. (I am executing _rsync_to_remote.py_ through terminal aplication from pyCharm, so I can see sync output in real time.)


### TODO:
- [ ] add GUI remove map for file_map.yaml
- [ ] change 'Instant sync' in SySU so it is launched via terminal, so you can see output script (Possible problem in Windows?)