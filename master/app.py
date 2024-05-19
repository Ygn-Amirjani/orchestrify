from flask import Flask
from flask_restful import Api
import json

from WorkerRegistrar import WorkerRegistrar
from WorkersList import WorkersList
from WorkerInfo import WorkerInfo

from database.RedisDB import Redis

# Load config file
with open('master/conf/config.json', mode='r') as config_file:
    CONFIG = json.load(config_file)


app = Flask(__name__)
api = Api(app)

app.debug = True

db = Redis()

api.add_resource(
    WorkerRegistrar,
    CONFIG.get('routes', {}).get('master', {}).get('register'),
    resource_class_kwargs={'repository': db}
)
api.add_resource(
    WorkersList,
    CONFIG.get('routes', {}).get('master', {}).get('list'),
    resource_class_kwargs={'repository': db}
)
api.add_resource(
    WorkerInfo,
    CONFIG.get('routes', {}).get('master', {}).get('info'),
    resource_class_kwargs={'repository': db}
)

if __name__ == "__main__":
    app.run(host=CONFIG.get('host'), port=CONFIG.get('port'))
