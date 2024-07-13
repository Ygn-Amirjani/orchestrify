import docker
from flask import request
from flask_restful import Resource
from typing import Any, Dict

class ImageRunner(Resource):
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

            # Print container details
            print(f"Successfully ran image: {image_name}")
            print(f"Container ID: {container.id}")
            print(container.logs().decode("utf-8"))

            return {
                "status": "ok",
                "image": image_name,
                "container_id": container.id,
                "container_name": container.name,
                "container_status": container.status
            }, 200

        except docker.errors.ImageNotFound as e:
            return {
                "status": "error",
                "message": f"Image not found: {image_name}. Error: {e}",
            }, 404

        except docker.errors.APIError as e:
            return {
                "status": "error",
                "message": f"Failed to run image: {image_name}. API Error: {e}",
            }, 500

        except docker.errors.ContainerError as e:
            return {
                "status": "error",
                "message": f"Container error: {e}",
            }, 500

        except docker.errors.DockerException as e:
            return {
                "status": "error",
                "message": f"Docker exception: {e}",
            }, 500

        except ValueError as e:
            return {
                "status": "error",
                "message": f"Invalid input: {e}",
            }, 400

        except Exception as e:
            return {
                "status": "error",
                "message": f"An unexpected error occurred: {e}",
            }, 500
