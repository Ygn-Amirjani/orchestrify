from flask_restful import Resource
from typing import Tuple, List

from db import db

class WorkerList(Resource):
    def get(self) -> Tuple[List[str], int]:
        """List of all registered workers"""
        return list(db.keys()), 200
