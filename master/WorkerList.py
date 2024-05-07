from flask_restful import Resource
from typing import Tuple, List

from db import DB

class WorkerList(Resource):
    def get(self) -> Tuple[List[str], int]:
        """List of all registered workers"""
        db = DB()
        return  db.get_all_ids(), 200