from flask import Flask
from flask_restful import Api

from WorkerRegistrar import WorkerRegistrar
from WorkersList import WorkersList
from WorkerInfo import WorkerInfo

from DataBase.RedisDB import Redis

app = Flask(__name__)
api = Api(app)

app.debug = True

db = Redis()

api.add_resource(
    WorkerRegistrar,
    '/worker',
    resource_class_kwargs={'repository': db}
)
api.add_resource(
    WorkersList,
    '/workers',
    resource_class_kwargs={'repository': db}
)
api.add_resource(
    WorkerInfo,
    '/worker/<worker_id>',
    resource_class_kwargs={'repository': db}
)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=18080)
