from flask_restful import Resource
from typing import Tuple, List
from master.database.Repository import Repository

class ContainersList(Resource):
    def __init__(self, repository: Repository) -> None:
        self.repository = repository

    def get(self) -> Tuple[List[str], int]:
        """List of all Containers."""
        all_keys = self.repository.read_all()

        container_keys = [key for key in all_keys
            if key.startswith("container:")]

        return container_keys, 200
