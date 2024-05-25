from flask_restful import Resource, reqparse
from typing import Tuple, Dict, Any
from database.Repository import Repository


class WorkerRegistrar(Resource):
    def __init__(self, repository: Repository) -> None:
        self.repository = repository

    def post(self) -> Tuple[Dict[str, Any], int]:
        """Saving worker information on the database"""
        parser = reqparse.RequestParser()
        parser.add_argument("id", type=str, required=True)
        parser.add_argument("ip", type=str, required=True)
        parser.add_argument("ram", type=int, required=True)
        parser.add_argument("cpu", type=int, required=True)
        parser.add_argument("status", type=str, required=True)
        args = parser.parse_args()

        self.repository.create(args["id"], args)

        return {"status": "ok", "id": args["id"]}, 200
