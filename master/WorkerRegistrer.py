from flask_restful import Resource, reqparse
from typing import Tuple, Dict, Any
from master.database.Repository import Repository

class WorkerRegistrer(Resource):
    def __init__(self, repository: Repository) -> None:
        self.repository = repository

    def post(self) -> Tuple[Dict[str, Any], int]:
        """Saving worker information on the database"""
        parser = reqparse.RequestParser()
        parser.add_argument("id", type=str, required=True)
        parser.add_argument("ip", type=str, required=True)
        parser.add_argument("ram-usage", type=int, required=True)
        parser.add_argument("cpu-usage", type=int, required=True)
        parser.add_argument("status", type=str, required=True)
        args = parser.parse_args()

        self.repository.create(f"worker:{args["id"]}:status", args)

        return {"status": "ok", "id": args["id"]}, 200
