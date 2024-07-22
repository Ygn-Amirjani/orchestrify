from flask_restful import Resource
import docker
import logging

from worker.conf.logging_config import setup_logging

class StatusSender(Resource):
    def __init__(self):
        self.client = docker.from_env()
        log_file = "logs/worker_app.log"
        setup_logging(log_file)
        self.logger = logging.getLogger(self.__class__.__name__)

    def get(self, container_id):
        try:
            container = self.client.containers.get(container_id)
            status = container.status
            self.logger.info(f"Container {container_id} status retrieved: {status}")
            return {"container_id": container_id, "status": status}, 200

        except docker.errors.NotFound:
            self.logger.error(f"Container {container_id} not found")
            return {"error": f"Container {container_id} not found"}, 404

        except docker.errors.APIError as e:
            self.logger.error(f"Error retrieving container {container_id} status: {e}")
            return {"error": "An error occurred while retrieving the container status"}, 500
