from flask_restful import Resource
from typing import Tuple, Dict, Any
from master.database.Repository import Repository

class WorkerInfo(Resource):
    def __init__(self, repository: Repository) -> None:
        self.repository = repository

    def get(self, worker_id: str) -> Tuple[Dict[str, Any], int]:
        """List of requested worker information"""
        if not worker_id.startswith("worker:"):
            return {"error": "Invalid worker ID"}, 400
        
        worker = self.repository.read(worker_id)
        
        if worker is None:
            return {"error": "Worker not found"}, 404
        
        if worker.get("status") != "RUNNING":
            return {"error": "Worker is not running"}, 400
        
        return worker, 200
