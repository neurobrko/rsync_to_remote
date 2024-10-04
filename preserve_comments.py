#!/usr/bin/env python3.12

import yaml

yaml_flle = "sync_conf_test.yaml"

with open(yaml_flle, "r") as f:
    config = yaml.safe_load(f)

with open(yaml_flle, "r") as f:
    content = f.readlines()

comments = []
for line in content:
    if "#" in line:
        comments.append(line)

config["rsync"]["host"] = "localhost"

with open(yaml_flle, "w") as f:
    yaml.dump(config, f, sort_keys=False)

with open(yaml_flle, "r") as f:
    new_content = f.readlines()

new_content = comments + ["---\n"] + new_content + ["..."]

with open(yaml_flle, "w") as f:
    f.writelines(new_content)
