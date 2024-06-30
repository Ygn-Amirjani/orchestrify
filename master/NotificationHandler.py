from flask_restful import Resource
from master.database.Repository import Repository
from flask import request

class NotificationHandler(Resource):
    def __init__(self, repository: Repository) -> None:
        self.repository = repository

    def post(self):
        master_url = request.get_json()
        print(master_url)
