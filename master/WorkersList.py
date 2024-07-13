from flask_restful import Resource, abort
from typing import Tuple, List
from master.database.Repository import Repository

class WorkersList(Resource):
    def __init__(self, repository: Repository) -> None:
        self.repository = repository

    def get(self) -> Tuple[List[str], int]:
        """List of all registered workers."""
        try:
            all_keys = self.repository.read_all()

            worker_keys = [key for key in all_keys if key.startswith("worker:")]

            return worker_keys, 200

        except Exception as e:
            return {"message": f"Failed to retrieve worker list: {e}"}, 500
