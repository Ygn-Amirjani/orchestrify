from flask_restful import Resource
from typing import Tuple, List
from DataBase.Repository import Repository

class WorkersList(Resource):
    def __init__(self, repository: Repository) -> None:
        self.repository = repository

    def get(self) -> Tuple[List[str], int]:
        """List of all registered workers"""
        return  self.repository.read_all(), 200
