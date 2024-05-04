from flask_restful import Resource
from typing import Tuple, Dict, Any

from db import db

class WorkerInformation(Resource):
    def get(self, worker_id) -> Tuple[Dict[str, Any], int]:
        """List of requested worker information"""
        if worker_id not in db:
            return {"error": "Worker not found"}, 404
        return db[worker_id], 200