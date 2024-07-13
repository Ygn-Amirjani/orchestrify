import docker.errors
from flask import request
from flask_restful import Resource
from typing import Any, Dict
import docker

class ImagePuller(Resource):
    def post(self) -> Dict[str, Any]:
        """Handle POST request to pull a Docker image."""
        try:
            image_name = request.get_json()
            if not image_name:
                return {"status": "error", "message": "Image name is required"}, 400

            # Create a Docker client
            client = docker.from_env()

            # Pull the image
            image = client.images.pull(image_name)

            # Print the pulled image details
            print(f"Successfully pulled image: {image_name}")
            print(f"Image ID: {image.id}")
            print(f"Tags: {', '.join(image.tags)}")

            return {"status": "ok", "image": image_name}, 200

        except docker.errors.ImageNotFound as e:
            return {
                "status": "error",
                "message": f"Image not found: {image_name}. Error: {e}",
            }, 404

        except docker.errors.APIError as e:
            return {
                "status": "error",
                "message": f"Failed to pull image: {image_name}. Error: {e}",
            }, 500

        except docker.errors.DockerException as e:
            return {
                "status": "error",
                "message": f"Docker exception occurred: {e}",
            }, 500

        except Exception as e:
            return {
                "status": "error",
                "message": f"An unexpected error occurred: {e}",
            }, 500
