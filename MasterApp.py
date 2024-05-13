from flask import Flask
from flask_restful import Api

from master.WorkerRegistration import WorkerRegistration
from master.WorkerList import WorkerList
from master.WorkerInformation import WorkerInformation

from Redis import Redis

app = Flask(__name__)
api = Api(app)

app.debug = True

db = Redis()

api.add_resource(
    WorkerRegistration,
    '/worker',
    resource_class_kwargs={'repository': db}
)
api.add_resource(
    WorkerList,
    '/workers',
    resource_class_kwargs={'repository': db}
)
api.add_resource(
    WorkerInformation,
    '/worker/<worker_id>',
    resource_class_kwargs={'repository': db}
)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=18080)
