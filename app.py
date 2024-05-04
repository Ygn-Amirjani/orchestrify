from flask import Flask
from flask_restful import Api

from master.WorkerRegistration import WorkerRegistration
from master.WorkerList import WorkerList
from master.WorkerInformation import WorkerInformation

app = Flask(__name__)
api = Api(app)

api.add_resource(
    WorkerRegistration,
    '/worker'
)
api.add_resource(
    WorkerList,
    '/workers'
)
api.add_resource(
    WorkerInformation,
    '/worker/<worker_id>'
)

if __name__ == "__main__":
    app.run(debug=True)
