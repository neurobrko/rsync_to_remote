# RSYNC SETTINGS
host = "10.122.58.49"
username = "root"
host_address = "117"
# port = f"13{host_address}"
port = "13117"
rsync_options = ["-rtvz", "--progress", "-e", f"ssh -p {port}"]
local_root_dir = "/home/marpauli/code/cisco/_SIMPLE"

# Specify dir to start browsing from
# local_root_dir is used if empty, if LRD empty GUI uses script dir
default_dir = ""

# SCRIPT SETTINGS
# set 0 to skip check
VM_check_timeout = 0
result_timeout = 0
date_format = "%Y-%m-%d %H:%M:%S"

# SYNC ALL FILES IN <file_map>
sync_all = False
# SYNC ALL FILES FROM SPECIFIED PROJECT
project = None
# LIST OF FILES TO SYNC
# WARNING: Must be list even with single item!
file_keys = []
# INFO: <sync_all> overrides <project>, <project> overrides <file_keys>

# CLI OUTPUT FORMATTING
GN = "\033[0;32m"  # green normal
GB = "\033[1;32m"  # green bold
RN = "\033[0;31m"  # red normal
RB = "\033[1;31m"  # red bold
CN = "\033[0;36m"  # cyan normal
CB = "\033[1;36m"  # cyan bold
WU = "\033[4;37m"  # white underline
BLD = "\033[1m"  # bold
UND = "\033[4m"  # underline
RST = "\033[0m"  # reset formatting
