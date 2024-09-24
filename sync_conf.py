# RSYNC SETTINGS
host = "10.122.58.49"
username = "root"
host_address = "138"
port = f"13{host_address}"
rsync_options = ("-rtvz", "--progress", "-e", f"ssh -p {port}")
local_root_dir = "/home/marpauli/code/cisco/_SIMPLE/"

# SCRIPT SETTINGS
VM_check_timeout = 3
result_timeout = 10
date_format = "%Y-%m-%d %H:%M:%S"

