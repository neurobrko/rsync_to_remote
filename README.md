# Synchronize files to remote
**Set of tools to manage and perform synchronization of files to remote system using rsync. Script also ouptuts 
its action to console and logs them.**

_**rsync_to_remote.py**_ - standalone CLI script to perform synchronization. Configuration is loaded from _sync_conf.yaml_, 
but can be altered using CLI arguments. See _rsync_to_remote.py -h_.

_**GUI_rsync_to_remote.py**_ - GUI tool for changing configuration saved in _sync_conf.py_. It also allows you to either 
run sync dw/o changing configuration, or alter configuration (one-time or permanently) or just save new configuration.

_**GUI_add_map.py**_ - synchronization uses list of file pairs stored in _file_map.yaml_ passed to rsync. Each pair is
subset of project. It gives you opportunity to sync all files in project, or just selected files throughout all projects.

_**GUI_show_log.py**_ - show log for last sync. Option to view complete log file.

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

### TODO:
- [ ] remove log files older than X days
- [ ] add GUI remove map for file_map.yaml
- [ ] create GUI wrapper for all tools (SyncSuite)