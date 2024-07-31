from flask import request
from flask_restful import Resource
import argparse
import ast
import logging

from master.database.Repository import Repository
from master.ContainersList import ContainersList
from master.WorkersList import WorkersList
from master.WorkerSelector import WorkerSelector
from master.ImageDeploymentHandler import ImageDeploymentHandler
from master.ContainerDeleter import ContainerDeleter
from master.conf.logging_config import setup_logging

class ContainerReallocator(Resource):
    def __init__(self, repository: Repository) -> None:
        self.repository = repository
        self.containers_list = ContainersList(repository)
        self.workers_list = WorkersList(repository)
        self.log_file = "logs/master_app.log"
        setup_logging(self.log_file)
        self.logger = logging.getLogger(self.__class__.__name__)

    def post(self):
        try:
            worker_info = request.get_json()

            if worker_info.get('status') != "INACTIVE":
                self.logger.info(f"Skipping worker {worker_info.get('id')} because it is not inactive")
                return f"Skipping worker {worker_info.get('id')}"

            container_list = self.find_containers_to_delete(worker_info.get('ip'))
            self.deploy_image(container_list)

        except Exception as e:
            self.logger.error(f"Error in post method: {str(e)}", exc_info=True)
            return {"error": "An error occurred during processing"}, 500

    def find_containers_to_delete(self, ip: str) -> list:
        try:
            container_keys, _ = self.containers_list.get()
            containers_to_delete = []

            for container_key in container_keys:
                container_info = self.repository.read(container_key)
                if container_info.get('status') != 'exited' and container_info.get('worker_ip') == ip:
                    if self.delete_container(container_info):
                        containers_to_delete.append(container_info)

            return containers_to_delete

        except Exception as e:
            self.logger.error(f"Error in find_containers_to_delete method: {str(e)}", exc_info=True)
            raise

    def delete_container(self, container_info) -> bool:
        try:
            container_deleter = ContainerDeleter(self.repository, container_info.get('id'))
            result = container_deleter.main()
            if result:
                _, status = result
                return status

            return False
        except Exception as e:
            self.logger.error(f"Error in delete_container method: {str(e)}", exc_info=True)
            raise

    def build_args(self, container_info) -> argparse.Namespace:
        """Build the arguments for deploying the container image."""
        try:
            port_mapping = None
            if container_info.get('port'):
                port_mapping = self.reformat_port(container_info.get('port'))

            env_mapping = None
            if container_info.get('environment'):
                env_mapping = eval(container_info.get('environment'))

            args_dict = {
                "image_name": container_info.get("image_name"),
                "name": container_info.get("name", None),
                "network": container_info.get("network_mode", None),
                "port": port_mapping ,
                "environment": env_mapping,
            }
            self.logger.info(f"Built args: {args_dict}")
            return argparse.Namespace(**args_dict)
        except Exception as e:
            self.logger.error(f"Exception occurred during build_args: {str(e)}", exc_info=True)
            raise

    def reformat_port(self, container_port_str: str):
        """Reformat the port information from the container info."""
        try:
            port_dict = ast.literal_eval(container_port_str)
            port_mapping = {f"{int(key.split('/')[0])}/tcp": value for key, value in port_dict.items()}
            self.logger.info(f"Reformatted port mapping: {port_mapping}")
            return port_mapping
        except Exception as e:
            self.logger.error(f"Exception occurred during reformat_port: {str(e)}", exc_info=True)
            raise

    def deploy_image(self, containers_list: str) -> None:
        try:
            workers, _ = self.workers_list.get()
            worker_selector = WorkerSelector(self.repository, workers)

            for container_info in containers_list:
                selected_worker = worker_selector.main()
                if not selected_worker:
                    self.logger.error(f"Error in find worker", exc_info=True) 
                args = self.build_args(container_info)
                image_handler = ImageDeploymentHandler(self.repository, args, selected_worker)
                image_handler.main()
        except Exception as e:
            self.logger.error(f"Error in deploy_image method: {str(e)}", exc_info=True)
            raise
