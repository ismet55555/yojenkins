#!/usr/bin/env python3

import yaml
import sys
import toml
from pprint import pprint

# Load YAML file
with open(sys.argv[1], 'r') as yaml_file:
    yaml_data = yaml.safe_load(yaml_file)

# Convert YAML to TOML
toml_data = toml.dumps(yaml_data)

pprint(toml_data)
print(toml_data)
