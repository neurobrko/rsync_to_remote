# Synchronize files to remote machine

### sync_conf
RSYNC SETTINGS
  - when editing port, always edit rsync option accordingly!
  - local_root_dir should ALWAYS contain valid path,
    BUT if empty, must be "" (same goes for default_dir)

SCRIPT SETTINGS
  - set timeouts to 0 to skip check
  - set default_dir to specify dir to start browsing from
    local_root_dir is used if empty, if LRD empty script parent dir is used

SYNC SETTINGS
  INFO: <sync_all> overrides <project>, <project> overrides <file_keys>
  - sync_all: sync all files in <file_map.yaml>; value: true/false
  - project: sync all files from specified project, null for None
  - file_keys: list of file pairs to sync
    WARNING: Must be list even with zero or single item! hint: empty_list: []

COLORS SETTINGS
   GN: green normal
   GB: green bold
   RN: red normal
   RB: red bold
   CN: cyan normal
   CB: cyan bold
   WU: white underline
   BLD: bold
   UND: underline
   RST: reset formatting

### TODO:
- [ ] rewrite this README
- [ ] remove log files older than X days
- [ ] update sync_conf.yaml from GUI
- [ ] add GUI remove for file_map.yaml