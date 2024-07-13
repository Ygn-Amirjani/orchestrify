from flask_restful import Resource, reqparse
from typing import Tuple, Dict, Any
from master.database.Repository import Repository

class WorkerRegistrer(Resource):
    def __init__(self, repository: Repository) -> None:
        self.repository = repository

    def post(self) -> Tuple[Dict[str, Any], int]:
        """Saving worker information on the database"""
        try:
            parser = reqparse.RequestParser()
            parser.add_argument("id", type=str, required=True)
            parser.add_argument("ip", type=str, required=True)
            parser.add_argument("ram-usage", type=int, required=True)
            parser.add_argument("cpu-usage", type=int, required=True)
            parser.add_argument("status", type=str, required=True)
            args = parser.parse_args()

            self.repository.create(f"worker:{args["id"]}:{args["ip"]}", args)

            return {"status": "ok", "id": args["id"]}, 200

        except KeyError as ke:
            return {"status": "error", "message": f"KeyError: {str(ke)}"}, 400

        except ValueError as ve:
            return {"status": "error", "message": f"ValueError: {str(ve)}"}, 400

        except Exception as e:
            return {"status": "error", "message": f"Internal Server Error: {str(e)}"}, 500
