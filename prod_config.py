import argparse
import os
from pathlib import Path
from itertools import chain

# Commandline stuff
parser = argparse.ArgumentParser()
parser.add_argument("--config", dest="config", type=str, help="Specify an alternate config file")
parser.add_argument("--debug", action='store_true', help="Print every incoming API event as JSON")
args = parser.parse_args()

# Read config files from the main file, and also from the drop-in directory
config_filepath = args.config or "prod.conf"
config_path = os.path.abspath(config_filepath)
config_path_dir = os.path.join(os.path.dirname(config_path), "{}.d".format(os.path.basename(config_path)))
config_filepaths = [config_path] + list(map(lambda x: os.path.join(config_path_dir, x), os.listdir(config_path_dir) if os.path.isdir(config_path_dir) else []))
config_lines = list(filter(lambda x: len(x) == 2 and len(x[0]) * len(x[1]) > 0, map(lambda x: x.split("#", 1)[0].strip().split(" ", 1), chain(*map(lambda x: Path(x).read_text().splitlines(), config_filepaths)))))

# Each config entry gets saved in an array associated by its key.
# Most settings will only use the last value, but the whole array can be accessed
ConfigEntries = {}
for line in config_lines:
    ConfigEntries[line[0]] = (ConfigEntries[line[0]] if line[0] in ConfigEntries.keys() else []) + [line[1]]

GetConfigString = lambda x: ConfigEntries[x][-1] if x in ConfigEntries.keys() else None
GetConfigInt = lambda x: int(GetConfigString(x))
GetConfigFloat = lambda x: float(GetConfigString(x))
GetConfigArray = lambda x: ConfigEntries[x] if x in ConfigEntries.keys() else []
