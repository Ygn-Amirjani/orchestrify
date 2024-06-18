from flask_restful import Resource, reqparse
from typing import Tuple, Dict, Any
from master.database.Repository import Repository

class WorkerUpdater(Resource):
    def __init__(self, repository: Repository) -> None:
        self.repository = repository

    def put(self, worker_id: str) -> Tuple[Dict[str, Any], int]:
        """Updating worker information in the database."""
        parser = reqparse.RequestParser()
        parser.add_argument("ip", type=str, required=True)
        parser.add_argument("ram-usage", type=int, required=True)
        parser.add_argument("cpu-usage", type=int, required=True)
        parser.add_argument("status", type=str, required=True)
        args = parser.parse_args()

        worker_status = f"worker:{worker_id}:status"
        worker_data = self.repository.read(worker_status)
        if not worker_data:
            return {"status": "error", "message": "Worker not found"}, 404

        self.repository.update(worker_status, args)

        return {"status": "ok", "id": worker_id}, 200
