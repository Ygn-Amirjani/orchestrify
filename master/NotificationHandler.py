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
        ip, port = self.extract_ip_port(master_url)

        if not self.update_workers_list(ip):
            return {"error": "worker not found"}, 404

        if not self.find_container_info(ip, port):
            return {"error": "container info not found"}, 404

        args = self.build_args()
        self.deploy_image(args)

    def extract_ip_port(self, master_url):
        split_url = master_url.split("//")[1]
        ip, port = split_url.split(":")
        return ip, port

    def update_workers_list(self, ip):
        worker_keys, status = self.workers_list.get()
        self.workers = [worker_key for worker_key in worker_keys if worker_key.split(":")[2] != ip]
        return bool(self.workers)

    def find_container_info(self, ip, port):
        container_keys, status = self.containers_list.get()
        for container_key in container_keys:
            self.container_info = self.repository.read(container_key)
            if self.container_info.get('worker_ip') == ip and self.container_info.get('port').split(': ')[1].strip('}') == port:
                return True
        return False

    def build_args(self):
        port_mapping = self.reformat_port(self.container_info.get('port'))
        args_dict = {
            "image_name": self.container_info.get("image_name"),
            "name": "nginx",
            "network": None,
            "port": port_mapping,
            "environment": self.container_info.get('environment'),
        }
        return argparse.Namespace(**args_dict)

    def reformat_port(self, container_port_str):
        temp_dict = ast.literal_eval("{'80/tcp': 80}")
        return {f"{int(key.split('/')[0])}/tcp": value for key, value in temp_dict.items()}

    def deploy_image(self, args):
        worker_selector = WorkerSelector(self.repository, self.workers)
        image_handler = ImageDeploymentHandler(self.repository, args, worker_selector.main())
        image_handler.main()
