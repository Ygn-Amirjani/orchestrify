import docker.models
import docker.models.containers
from flask import request
from flask_restful import Resource
from typing import Any, Dict

import docker


class ImageRunner(Resource):
    def post(self) -> Dict[str, Any]:
        try:
            image_name = request.get_json()
            if not image_name:
                return {"status": "error", "message": "Image name is required"}, 400

            # Create a Docker client
            client = docker.from_env()
            # Pull the image
            container: docker.models.containers.Container = client.containers.run(
                image_name, detach=True
            )

            # Print the pulled image details
            print(f"Successfully run image: {image_name}")
            print(f"Container ID: {container.id}")
            print(container.logs().decode("utf-8"))

            return {
                "status": "ok",
                "image": image_name,
                "container_id": container.id,
            }, 200
        except docker.errors.APIError as e:
            return {
                "status": "error",
                "message": f"Failed to pull image: {image_name}. Error: {e}",
            }, 500
