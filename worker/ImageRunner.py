from flask import request
from flask_restful import Resource
from typing import Any, Dict
from worker.conf.logging_config import setup_logging

import docker
import logging

class ImageRunner(Resource):
    def __init__(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)

    def post(self) -> Dict[str, Any]:
        try:
            data = request.get_json()
            if not data or "image_name" not in data:
                return {"status": "error", "message": "Image name is required"}, 400

            image_name = data["image_name"]
            container_name = data.get("name", None)
            network_mode = data.get("network_mode", None)
            port_bindings = data.get("port", None)
            environment = data.get("environment", None)

            # Set up logging for this specific class
            log_file = f'logs/{image_name}.log'
            setup_logging(log_file)
            self.logger.info('Imge Runner is Runnig')

            # Create a Docker client
            client = docker.from_env()

            # Prepare kwargs for container run
            kwargs = {
                "image": image_name,
                "detach": True
            }

            if container_name:
                kwargs["name"] = container_name

            if network_mode:
                kwargs["network_mode"] = network_mode
            
            if port_bindings:
                kwargs["ports"] = port_bindings

            if environment:
                kwargs["environment"] = environment

            # Run the container
            container = client.containers.run(**kwargs)

            # Log the ontainer details
            self.logger.info(f"Successfully ran image: {image_name}")
            self.logger.info(f"Container ID: {container.id}")
            self.logger.info(container.logs().decode("utf-8"))

            return {
                "status": "ok",
                "image": image_name,
                "container_id": container.id,
                "container_name": container.name,
                "container_status": container.status
            }, 200

        except docker.errors.ImageNotFound as e:
            self.logger.error(f"Image not found: {image_name}. Error: {e}")
            return {
                "status": "error",
                "message": f"Image not found: {image_name}. Error: {e}",
            }, 404

        except docker.errors.APIError as e:
            self.logger.error(f"Failed to run image: {image_name}. API Error: {e}")
            return {
                "status": "error",
                "message": f"Failed to run image: {image_name}. API Error: {e}",
            }, 500

        except docker.errors.ContainerError as e:
            self.logger.error(f"Container error: {e}")
            return {
                "status": "error",
                "message": f"Container error: {e}",
            }, 500

        except docker.errors.DockerException as e:
            self.logger.error(f"Docker exception: {e}")
            return {
                "status": "error",
                "message": f"Docker exception: {e}",
            }, 500

        except ValueError as e:
            self.logger.error(f"Invalid input: {e}")
            return {
                "status": "error",
                "message": f"Invalid input: {e}",
            }, 400

        except Exception as e:
            self.logger.error(f"An unexpected error occurred: {e}")
            return {
                "status": "error",
                "message": f"An unexpected error occurred: {e}",
            }, 500
