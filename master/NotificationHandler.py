from flask_restful import Resource
from flask import request
from typing import List, Dict, Any, Union, Tuple

from master.database.Repository import Repository
from master.ContainersList import ContainersList
from master.WorkersList import WorkersList
from master.WorkerSelector import WorkerSelector
from master.ImageDeploymentHandler import ImageDeploymentHandler
from master.conf.logging_config import setup_logging

import argparse
import ast
import logging

class NotificationHandler(Resource):
    def __init__(self, repository: Repository) -> None:
        self.repository = repository
        self.containers_list = ContainersList(repository)
        self.workers_list = WorkersList(repository)
        self.workers: List[str] = []
        self.container_info: Union[Dict[str, Any], None] = None

        # Set up logging
        log_file = 'logs/proxy.log'
        setup_logging(log_file)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info('NotificationHandler initialized')

    def post(self) -> Tuple[Dict[str, str], int]:
        """Handle POST requests to process notifications about container and worker status."""
        try:
            containers_info = request.get_json()
            self.logger.debug(f"Received request data: {containers_info}")

            ips = containers_info.get("ip")
            port = containers_info.get("port")

            if not self.update_workers_list(ips):
                self.logger.error("The response time of this container is more than 50ms in all workers")
                return {
                    "error": "The response time of this container is more than 50ms in all workers",
                    "status": "Please add the new worker to the cluster"
                }, 404

            if not self.find_container_info(ips, port):
                self.logger.error("Container info not found")
                return {"error": "container info not found"}, 404

            try:
                args = self.build_args()
                self.deploy_image(args)
            except Exception as e:
                self.logger.error(f"Problem for running container: {str(e)}")
                return {"error": f"problem for running container: {str(e)}"}, 500

            self.logger.info("Container Running on another worker")
            return {"status": "Container Running on another worker"}, 200

        except Exception as e:
            self.logger.error(f"Exception occurred during POST request: {str(e)}")
            return {"error": f"Internal server error: {str(e)}"}, 500

    def update_workers_list(self, ips: List[str]) -> bool:
        """Update the workers list by removing the workers whose IPs are in the given list."""
        try:
            worker_keys, status = self.workers_list.get()
            self.logger.debug(f"Worker keys: {worker_keys}, Status: {status}")

            self.workers = [worker_key for worker_key in worker_keys if worker_key.split(":")[2] not in ips]
            self.logger.debug(f"Updated workers list: {self.workers}")

            return bool(self.workers)

        except Exception as e:
            self.logger.error(f"Exception occurred during update_workers_list: {str(e)}")
            raise

    def find_container_info(self, ips: List[str], port: str) -> bool:
        """Find the container information based on the given IPs and port."""
        try:
            container_keys, status = self.containers_list.get()
            self.logger.debug(f"Container keys: {container_keys}, Status: {status}")

            for container_key in container_keys:
                self.container_info = self.repository.read(container_key)
                self.logger.debug(f"Read container info: {self.container_info}")

                if not self.container_info.get('port'):
                    continue

                if self.container_info.get('port').split(': ')[1].strip('}') == port:
                    if any(self.container_info.get('worker_ip') == ip for ip in ips):
                        self.logger.info(f"Found matching container info: {self.container_info}")
                        return True

            self.logger.warning("No matching container info found")
            return False

        except Exception as e:
            self.logger.error(f"Exception occurred during find_container_info: {str(e)}")
            raise

    def build_args(self) -> argparse.Namespace:
        """Build the arguments for deploying the container image."""
        try:
            port_mapping = self.reformat_port(self.container_info.get('port'))
            args_dict = {
                "image_name": self.container_info.get("image_name"),
                "name": "test",
                "network": None,
                "port": port_mapping,
                "environment": self.container_info.get('environment'),
            }
            self.logger.debug(f"Built args: {args_dict}")
            return argparse.Namespace(**args_dict)

        except Exception as e:
            self.logger.error(f"Exception occurred during build_args: {str(e)}")
            raise

    def reformat_port(self, container_port_str: str) -> Dict[str, Any]:
        """Reformat the port information from the container info."""
        try:
            temp_dict = ast.literal_eval("{'80/tcp': 1234}")
            port_mapping = {f"{int(key.split('/')[0])}/tcp": value for key, value in temp_dict.items()}
            self.logger.debug(f"Reformatted port mapping: {port_mapping}")
            return port_mapping

        except Exception as e:
            self.logger.error(f"Exception occurred during reformat_port: {str(e)}")
            raise

    def deploy_image(self, args: argparse.Namespace) -> None:
        """Deploy the container image using the provided arguments."""
        try:
            worker_selector = WorkerSelector(self.repository, self.workers)
            selected_worker = worker_selector.main()
            self.logger.info(f"Selected worker: {selected_worker}")

            image_handler = ImageDeploymentHandler(self.repository, args, selected_worker)
            image_handler.main()

        except Exception as e:
            self.logger.error(f"Exception occurred during deploy_image: {str(e)}")
            raise
