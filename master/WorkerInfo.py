from flask_restful import Resource
from typing import Tuple, Dict, Any
from master.database.Repository import Repository
from master.WorkersList import WorkersList

class WorkerInfo(Resource):
    def __init__(self, repository: Repository) -> None:
        self.repository = repository
        self.workers_list = WorkersList(repository)

    def get(self, worker_id: str) -> Tuple[Dict[str, Any], int]:
        """List of requested worker information"""
        worker_keys, status = self.workers_list.get()
        for worker_key in worker_keys:
            if worker_id == worker_key.split(':')[1]:
                return self.repository.read(worker_key), 200

        return {"error": "Worker not found"}, 404
