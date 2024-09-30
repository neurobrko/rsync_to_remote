# RSYNC SETTINGS
host = "10.122.58.49"
username = "root"
host_address = "138"
port = f"13{host_address}"
rsync_options = ["-rtvz", "--progress", "-e", f"ssh -p {port}"]
local_root_dir = "/home/marpauli/code/cisco/_SIMPLE/"

# SCRIPT SETTINGS
VM_check_timeout = 3  # set 0 to skip check
result_timeout = 10  # set 0 to skip end result check
date_format = "%Y-%m-%d %H:%M:%S"

# SYNC ALL FILES IN <file_map>
sync_all = False
# SYNC ALL FILES FROM SPECIFIED PROJECT
project = None
# LIST OF FILES TO SYNC
# WARNING: Must be list even with single item!
file_keys = [99, 98]

# INFO: <sync_all> overrides <project>, <project> overrides <file_keys>

# FILE MAPPING
# dict = {"project": {num: ["source", "target"]}}
# WARNING: num MUST be unique!
file_map = {
    "test": {
        99: [
            "/home/marpauli/code/cisco/rsync_to_VM/test_rsync/src/test.txt",
            "/home/marpauli/code/cisco/rsync_to_VM/test_rsync/trg/test.txt",
        ],
        98: [
            "/home/marpauli/code/cisco/rsync_to_VM/test_rsync/src/source.txt",
            "/home/marpauli/code/cisco/rsync_to_VM/test_rsync/trg/source.txt",
        ],
    },
    "6930": {
        1: [
            "drivers/runtime/lvm_maximize_root_volume.py",
            "/usr/local/bin/lvm-maximize-root-volume.py",
        ],
        2: [
            "drivers/runtime/systemd-services/virl2-initial-setup.py",
            "/usr/local/bin/virl2-initial-setup.py",
        ],
    },
    "6931": {
        3: [
            "drivers/simple_drivers/low_level_driver/host_statistics.py",
            "/var/local/virl2/.local/lib/python3.12/site-packages/simple_drivers/low_level_driver/host_statistics.py",
        ],
        4: [
            "drivers/simple_drivers/low_level_driver/accessors/grpc_lld_accessor.py",
            "/var/local/virl2/.local/lib/python3.12/site-packages/simple_drivers/low_level_driver/accessors/grpc_lld_accessor.py",
        ],
        5: [
            "core/simple_core/controller/events.py",
            "/var/local/virl2/.local/lib/python3.12/site-packages/simple_core/controller/events.py",
        ],
    },
    "6961": {
        6: [
            "simple_ui/simple_ui/http_handlers.py",
            "/var/local/virl2/.local/lib/python3.12/site-packages/simple_ui/http_handlers.py",
        ],
        7: [
            "packaging/CONFIG/nginx/controller.conf",
            "/etc/nginx/conf.d/controller.conf",
        ],
        8: [
            "simple_ui/simple_ui/swagger/api_disk_images.yaml",
            "/var/local/virl2/.local/lib/python3.12/site-packages/simple_ui/swagger/api_disk_images.yaml",
        ],
        9: [
            "core/simple_core/core_driver/accessors/base_driver_accessor.py",
            "/var/local/virl2/.local/lib/python3.12/site-packages/simple_core/core_driver/accessors/base_driver_accessor.py",
        ],
        10: [
            "simple_ui/simple_ui/exception_handling.py",
            "/var/local/virl2/.local/lib/python3.12/site-packages/simple_ui/exception_handling.py",
        ],
        11: [
            "core/simple_core/node_definitions/image_definitions/image_definition_manager.py",
            "/var/local/virl2/.local/lib/python3.12/site-packages/simple_core/node_definitions/image_definitions/image_definition_manager.py",
        ],
        12: [
            "core/simple_core/core_driver/servers/utils.py",
            "/var/local/virl2/.local/lib/python3.12/site-packages/simple_core/core_driver/servers/utils.py",
        ],
    },
    "OVA": {
        13: [
            "/home/marpauli/code/cisco/fix_OVA/fix_OVA.py",
            "/home/marpauli/fix_OVA.py",
        ],
    },
}

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
