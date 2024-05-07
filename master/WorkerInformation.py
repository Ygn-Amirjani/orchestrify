from flask_restful import Resource
from typing import Tuple, Dict, Any

from db import DB

class WorkerInformation(Resource):
    def get(self, worker_id) -> Tuple[Dict[str, Any], int]:
        """List of requested worker information"""
        db = DB()
        return db.load_data(worker_id), 200