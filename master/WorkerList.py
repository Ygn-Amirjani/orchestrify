from flask import jsonify
from flask_restful import Resource

from db import db

class WorkerList(Resource):
    def get(self):
        """List of all registered workers"""
        return list(db.keys()), 200
