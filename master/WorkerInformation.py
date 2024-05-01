from flask import jsonify
from flask_restful import Resource

from db import db

class WorkerInformation(Resource):
    def get(self, worker_id):
        """List of requested worker information"""
        if worker_id not in db:
            return {"error": "Worker not found"}, 404
        return db[worker_id], 200