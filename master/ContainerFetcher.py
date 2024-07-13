from master.database.Repository import Repository
from master.ContainersList import ContainersList
from flask_restful import Resource
from flask import request
from typing import List, Dict, Tuple, Any, Union

class ContainerFetcher(Resource):
    def __init__(self, repository: Repository) -> None:
        self.repository = repository
        self.containers_list = ContainersList(repository)
        self.container_port: Union[str, None] = None
        self.ips: List[str] = []

    def post(self) -> Tuple[Dict[str, Union[str, List[str]]], int]:
        """Handle POST requests to fetch container information."""
        data = request.get_json()

        container_keys, status = self.containers_list.get()
        for container_key in container_keys:
            if container_key.split(":")[1] != data:
                continue

            container_info = self.repository.read(container_key)
            self.container_port = container_info.get('port').split(': ')[1].strip('}')
            self.ips.append(container_info.get("worker_ip"))

        return {"status": "ok", "port": self.container_port, "ips": self.ips}, 200
