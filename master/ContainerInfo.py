from flask_restful import Resource
from typing import Tuple, Dict, Any
from master.database.Repository import Repository
from master.ContainersList import ContainersList

class ContainerInfo(Resource):
    def __init__(self, repository: Repository) -> None:
        self.repository = repository
        self.containers_list = ContainersList(repository)

    def get(self, container_id: str) -> Tuple[Dict[str, Any], int]:
        """Retrieve information of the requested container."""
        try:
            container_keys, status = self.containers_list.get()

            for container_key in container_keys:
                if container_id == container_key.split(':')[2]:
                    container_info = self.repository.read(container_key)
                    if container_info:
                        return container_info, 200
                    else:
                        return {"error": "Container information not found in the database."}, 404

            return {"error": f"Container with ID '{container_id}' not found."}, 404

        except KeyError as ke:
            return {"error": f"KeyError: {str(ke)}"}, 400

        except ValueError as ve:
            return {"error": f"ValueError: {str(ve)}"}, 400

        except Exception as e:
            return {"error": f"Internal Server Error: {str(e)}"}, 500
