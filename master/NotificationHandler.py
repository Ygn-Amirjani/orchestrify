from flask_restful import Resource
from flask import request
from master.database.Repository import Repository
from master.ContainersList import ContainersList
from master.WorkersList import WorkersList
from master.WorkerSelector import WorkerSelector
from master.ImageDeploymentHandler import ImageDeploymentHandler
from typing import List, Dict, Any, Union, Tuple

import argparse
import ast

class NotificationHandler(Resource):
    def __init__(self, repository: Repository) -> None:
        self.repository = repository
        self.containers_list = ContainersList(repository)
        self.workers_list = WorkersList(repository)
        self.workers: List[str] = []
        self.container_info: Union[Dict[str, Any], None] = None

    def post(self) -> Tuple[Dict[str, str], int]:
        """Handle POST requests to process notifications about container and worker status."""
        try:
            containers_info = request.get_json()
            ips = containers_info.get("ip")
            port = containers_info.get("port")

            if not self.update_workers_list(ips):
                return {
                    "error": "The response time of this container is more than 50ms in all workers",
                    "status": "Please add the new worker to the cluster"
                }, 404

            if not self.find_container_info(ips, port):
                return {"error": "container info not found"}, 404

            try:
                args = self.build_args()
                self.deploy_image(args)
            except Exception as e:
                return {"error": f"problem for running container: {str(e)}"}, 500

            return {"status": "Container Running on another worker"}, 200

        except Exception as e:
            print(f"Exception occurred during POST request: {str(e)}")
            return {"error": f"Internal server error: {str(e)}"}, 500

    def update_workers_list(self, ips: List[str]) -> bool:
        """Update the workers list by removing the workers whose IPs are in the given list."""
        try:
            worker_keys, status = self.workers_list.get()
            self.workers = [worker_key for worker_key in worker_keys if worker_key.split(":")[2] not in ips]
            return bool(self.workers)

        except Exception as e:
            print(f"Exception occurred during update_workers_list: {str(e)}")
            raise

    def find_container_info(self, ips: List[str], port: str) -> bool:
        """Find the container information based on the given IPs and port."""
        try:
            container_keys, status = self.containers_list.get()
            for container_key in container_keys:
                self.container_info = self.repository.read(container_key)
                if self.container_info.get('port').split(': ')[1].strip('}') == port:
                    if any(self.container_info.get('worker_ip') == ip for ip in ips):
                        return True
            return False

        except Exception as e:
            print(f"Exception occurred during find_container_info: {str(e)}")
            raise

    def build_args(self) -> argparse.Namespace:
        """Build the arguments for deploying the container image."""
        try:
            port_mapping = self.reformat_port(self.container_info.get('port'))
            args_dict = {
                "image_name": self.container_info.get("image_name"),
                "name": self.container_info.get("name"),
                "network": self.container_info.get("network_mode"),
                "port": port_mapping,
                "environment": self.container_info.get('environment'),
            }
            return argparse.Namespace(**args_dict)

        except Exception as e:
            print(f"Exception occurred during build_args: {str(e)}")
            raise

    def reformat_port(self, container_port_str: str) -> Dict[str, Any]:
        """Reformat the port information from the container info."""
        try:
            temp_dict = ast.literal_eval(container_port_str)
            return {f"{int(key.split('/')[0])}/tcp": value for key, value in temp_dict.items()}

        except Exception as e:
            print(f"Exception occurred during reformat_port: {str(e)}")
            raise

    def deploy_image(self, args: argparse.Namespace) -> None:
        """Deploy the container image using the provided arguments."""
        try:
            worker_selector = WorkerSelector(self.repository, self.workers)
            image_handler = ImageDeploymentHandler(self.repository, args, worker_selector.main())
            image_handler.main()

        except Exception as e:
            print(f"Exception occurred during deploy_image: {str(e)}")
            raise
