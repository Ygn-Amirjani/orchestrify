from flask import request
from flask_restful import Resource
from typing import Any, Dict
from worker.conf.logging_config import setup_logging

import docker.errors
import docker
import logging

class ImagePuller(Resource):
    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)

    def post(self) -> Dict[str, Any]:
        """Handle POST request to pull a Docker image."""
        try:
            image_name = request.get_json()

            # Set up logging for Image Puller
            log_file = f'logs/{image_name}.log'
            setup_logging(log_file)
            self.logger.info('Imge Puller is Runnig')

            if not image_name:
                self.logger.error("Image name is required")
                return {"status": "error", "message": "Image name is required"}, 400

            # Create a Docker client
            client = docker.from_env()

            # Pull the image
            image = client.images.pull(image_name)

            # Log the pulled image details
            self.logger.info(f"Successfully pulled image: {image_name}")
            self.logger.info(f"Image ID: {image.id}")
            self.logger.info(f"Tags: {', '.join(image.tags)}")

            return {"status": "ok", "image": image_name}, 200

        except docker.errors.ImageNotFound as e:
            self.logger.error(f"Image not found: {image_name}. Error: {e}")
            return {
                "status": "error",
                "message": f"Image not found: {image_name}. Error: {e}",
            }, 404

        except docker.errors.APIError as e:
            self.logger.error(f"Failed to pull image: {image_name}. Error: {e}")
            return {
                "status": "error",
                "message": f"Failed to pull image: {image_name}. Error: {e}",
            }, 500

        except docker.errors.DockerException as e:
            self.logger.error(f"Docker exception occurred: {e}")
            return {
                "status": "error",
                "message": f"Docker exception occurred: {e}",
            }, 500

        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
            return {
                "status": "error",
                "message": f"An unexpected error occurred: {e}",
            }, 500
