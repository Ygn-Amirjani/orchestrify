from flask import Flask
from flask_restful import Api
from master.conf.config import CONFIG

from master.WorkerRegistrar import WorkerRegistrar
from master.WorkerUpdater import WorkerUpdater
from master.WorkersList import WorkersList
from master.WorkerInfo import WorkerInfo

from master.database.RedisDB import Redis


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
    WorkerUpdater,
    CONFIG.get('routes', {}).get('master', {}).get('update'),
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
