from flask_restful import Resource
from worker.conf.logging_config import setup_logging

import docker
import logging

class ContainerRemover(Resource):
    def __init__(self) -> None:
        self.log_file = f'logs/worker_app.log'
        setup_logging(self.log_file)
        self.logger = logging.getLogger(self.__class__.__name__)

    def delete(self, container_id):
        client = docker.from_env()
        try:
            container = client.containers.get(container_id)
            container.remove(force=True)
            self.logger.info(f"Container {container_id} deleted successfully")
            return {'message': f'Container {container_id} deleted successfully'}, 200

        except docker.errors.NotFound:
            self.logger.warning(f"Container {container_id} not found")
            return {'error': 'Container not found'}, 404

        except docker.errors.APIError as e:
            self.logger.error(f"API error while deleting container {container_id}: {str(e)}")
            return {'error': str(e)}, 500

        except Exception as e:
            self.logger.error(f"Unexpected error while deleting container {container_id}: {str(e)}")
            return {'error': 'An unexpected error occurred'}, 500
