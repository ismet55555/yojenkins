#!/usr/bin/env python3

import toml
import sys
from pprint import pprint

# Load toml file
with open(sys.argv[1], 'r') as f:
    toml_file = toml.load(f)

# Print toml file to stdout
print(toml.dumps(toml_file))

pprint(toml_file)
