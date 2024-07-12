from flask_restful import Resource
from flask import request
from master.database.Repository import Repository
from master.ContainersList import ContainersList
from master.WorkersList import WorkersList
from master.WorkerSelector import WorkerSelector
from master.ImageDeploymentHandler import ImageDeploymentHandler

import argparse
import ast

class NotificationHandler(Resource):
    def __init__(self, repository: Repository) -> None:
        self.repository = repository
        self.containers_list = ContainersList(repository)
        self.workers_list = WorkersList(repository)
        self.workers = list()
        self.container_info = None

    def post(self):
        master_url = request.get_json()
        ip = master_url.split("//")[1].split(":")[0]
        port = master_url.split("//")[1].split(":")[1]

        worker_keys, status = self.workers_list.get()
        self.workers.extend(
            worker_key for worker_key in worker_keys 
            if worker_key.split(":")[2] != ip
        )
        if not self.workers:
            return {"error": "worker not found"}, 404

        container_keys, status = self.containers_list.get()
        for container_key in container_keys:
            self.container_info = self.repository.read(container_key)
            
            if self.container_info.get('worker_ip') != ip:
                continue
            
            container_port_str = self.container_info.get('port')
            if not container_port_str:
                continue
            
            container_port = container_port_str.split(': ')[1].strip('}')
            if container_port == port:
                break

        if not self.container_info:
            return {"error": "container info not found"}, 404

        string_dict = "{'80/tcp': 80}" #container_port_str

        # Reformat the dictionary with f-string keys
        temp_dict = ast.literal_eval(string_dict)
        formatted_dict = {f"{int(key.split('/')[0])}/tcp": value for key, value in temp_dict.items()}
        args_dict = {
            "image_name": self.container_info.get("image_name"),
            "name": "nginx",
            "network": None,
            "port": formatted_dict,
            "environment": self.container_info.get('environment'),
        }
        args = argparse.Namespace(**args_dict)

        worker_selector = WorkerSelector(self.repository, self.workers)
        imageHandler = ImageDeploymentHandler(self.repository, args, worker_selector.main())
        imageHandler.main()
