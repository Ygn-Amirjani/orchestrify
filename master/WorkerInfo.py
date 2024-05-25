from flask_restful import Resource
from typing import Tuple, Dict, Any
from master.database.Repository import Repository

class WorkerInfo(Resource):
    def __init__(self, repository: Repository) -> None:
        self.repository = repository

    def get(self, worker_id) -> Tuple[Dict[str, Any], int]:
        """List of requested worker information"""
        return self.repository.read(worker_id), 200
