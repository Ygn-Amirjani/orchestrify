from flask_restful import Resource
from typing import Tuple, List
from master.database.Repository import Repository

class WorkersList(Resource):
    def __init__(self, repository: Repository) -> None:
        self.repository = repository

    def get(self) -> Tuple[List[str], int]:
        """List of all registered workers"""
        all_keys = self.repository.read_all()
        worker_keys = [key for key in all_keys
            if key.startswith("worker:") and key.endswith("status")]
        return worker_keys, 200
