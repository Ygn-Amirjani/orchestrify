from flask_restful import Resource
from typing import Tuple, Dict, Any
from master.database.Repository import Repository
from master.ContainersList import ContainersList

class ContainerInfo(Resource):
    def __init__(self, repository: Repository) -> None:
        self.repository = repository
        self.containers_list = ContainersList(repository)

    def get(self, container_id: str) -> Tuple[Dict[str, Any], int]:
        """List of requested container information"""
        container_keys, status = self.containers_list.get()
        for container_key in container_keys:
            if container_id == container_key.split(':')[2]:
                return self.repository.read(container_key), 200

        return {"error": "Container not found"}, 404
