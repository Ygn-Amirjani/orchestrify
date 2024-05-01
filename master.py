from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse

app = Flask(__name__)
api = Api(app)

db = {}

class WorkerRegistration(Resource):
    def post(self):
        """Saving worker information on the database"""
        parser = reqparse.RequestParser()
        parser.add_argument("id", type=str, required=True)
        parser.add_argument("ip", type=str, required=True)
        parser.add_argument("ram", type=int, required=True)
        parser.add_argument("cpu", type=int, required=True)
        parser.add_argument("status", type=str, required=True)
        args = parser.parse_args()

        worker_id = args["id"]
        db[worker_id] = {
            "ip": args["ip"],
            "ram": args["ram"],
            "cpu": args["cpu"],
            "status": args["status"],
        }
        return {"status": "ok", "id": worker_id}, 200
    
class WorkerList(Resource):
    def get(self):
        """List of all registered workers"""
        return list(db.keys()), 200

class Worker(Resource):
    def get(self, worker_id):
        """List of requested worker information"""
        if worker_id not in db:
            return {"error": "Worker not found"}, 404
        return db[worker_id], 200

api.add_resource(WorkerRegistration, "/worker")
api.add_resource(WorkerList, "/workers")
api.add_resource(Worker, "/worker/<string:worker_id>")

if __name__ == "__main__":
    app.run(debug=True)
