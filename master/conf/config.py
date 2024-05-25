import json

# Load config file
with open('master/conf/config.json', mode='r') as config_file:
    CONFIG = json.load(config_file)


# Access Redis configuration
REDIS_HOST = CONFIG['redis']['host']
REDIS_PORT = CONFIG['redis']['port']
