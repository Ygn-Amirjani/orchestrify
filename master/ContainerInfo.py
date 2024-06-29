from flask_restful import Resource
from typing import Tuple, Dict, Any
from master.database.Repository import Repository

class ContainerInfo(Resource):
    def __init__(self, repository: Repository) -> None:
        self.repository = repository

    def get(self, container_id: str) -> Tuple[Dict[str, Any], int]:
        """List of requested container information"""
        if not container_id.startswith("container:"):
            return {"error": "Invalid container ID"}, 400
        
        container = self.repository.read(container_id)
        
        if container is None:
            return {"error": "Worker not found"}, 404
        
        return container, 200
