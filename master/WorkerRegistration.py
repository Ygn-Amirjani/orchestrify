from flask_restful import Resource, reqparse
from typing import Tuple,Dict, Any

from db import db

class WorkerRegistration(Resource):
    def post(self)-> Tuple[Dict[str, Any], int]:
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
    