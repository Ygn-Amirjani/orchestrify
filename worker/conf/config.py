import json

# Load config file
with open('worker/conf/config.json', mode='r') as config_file:
    CONFIG = json.load(config_file)
