from flask_restful import Resource
from master.database.Repository import Repository
from master.ContainersList import ContainersList
from master.conf.logging_config import setup_logging

import requests
import logging

class ContainerDeleter(Resource):
    def __init__(self, repository: Repository) -> None:
        self.repository = repository
        self.containers_list = ContainersList(repository)
        self.log_file = "logs/master_app.log"
        setup_logging(self.log_file)
        self.logger = logging.getLogger(self.__class__.__name__)

    def delete(self, container_id: str):
        try:
            container_keys, status = self.containers_list.get()
            if status != 200:
                self.logger.error(f"Failed to get container keys: {status}")
                return {'error': 'Failed to get container keys'}, 500
            
            for container_key in container_keys:
                container_info = self.repository.read(container_key)
                if container_info is None:
                        self.logger.error(f"Container info not found for key: {container_key}")
                        return {'error': 'Container info not found'}, 404

                if container_id == container_key.split(':')[2] or container_id == container_info.get('id'):
                    self.repository.delete(container_key)
                    self.logger.info(f"Deleted container key from repository: {container_key}")

                    key = f"http://{container_info.get('worker_ip')}:18081/del/{container_id}"
                    response = self.delete_container(key)
                    if response.status_code == 200:
                        self.logger.info(f"Successfully deleted container for worker {container_info.get('worker_ip')}")
                    else:
                        self.logger.error(f"Failed to delete container for worker {container_info.get('worker_ip')} : {response.content}")
                        return {'error': 'Failed to delete container on worker'}, response.status_code

                    return container_info, 200

            self.logger.warning(f"Container ID {container_id} not found in the container keys")
            return {'error': 'Container not found'}, 404
        
        except requests.RequestException as e:
            self.logger.error(f"RequestException occurred: {str(e)}")
            return {'error': 'RequestException occurred'}, 500

        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {str(e)}")
            return {'error': 'An unexpected error occurred'}, 500

    def delete_container(self, container: str) -> requests.Response:
        """Perform a DELETE request."""
        try:
            response = requests.delete(container)
            response.raise_for_status()
            self.logger.info(f"DELETE request to {container} successful")
            return response

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error during DELETE request to {container}: {e}")
            raise
