from flask import request
from flask_restful import Resource
import docker

class PullImage(Resource):
    def post(self):
        try:
            # Parse the JSON data from request
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
        except docker.errors.APIError as e:
            return {"status": "error", "message": f"Failed to pull image: {image_name}. Error: {e}"}, 500
