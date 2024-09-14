from flask_restful import Resource, request
from flask import jsonify
from master.ImageDeploymentHandler import ImageDeploymentHandler
from master.WorkersList import WorkersList
from master.WorkerSelector import WorkerSelector
from master.database.Repository import Repository
from typing import List, Dict, Any, Union, Tuple

import argparse
import ast

class DeployImage(Resource):
    def __init__(self, repository: Repository) -> None:
        self.repository = repository

    def post(self):
        """Handle image deployment requests from the frontend."""
        try:
            json_data = request.get_json()

            # If port is provided, reformat it, otherwise set it to None
            port_mapping = self.reformat_port(json_data.get('port', None))

            # If environment variables are provided, reformat them
            env_mapping = None
            if json_data.get('environment'):
                env_mapping = eval(json_data.get('environment'))

            # Transform parsed arguments into an argparse.Namespace object
            args = argparse.Namespace(
                image_name=json_data.get('image_name'),
                name=json_data.get('name', None),
                network=json_data.get('network', None),
                port=port_mapping,
                environment=env_mapping
            )

            # Initialize the ImageDeploymentHandler
            workers_list = WorkersList(self.repository)
            workers, status = workers_list.get()
            worker_selector = WorkerSelector(self.repository, workers)
            image_handler = ImageDeploymentHandler(self.repository, args, worker_selector.main())

            # Execute the image deployment
            image_handler.main()

            return {'message': 'Image deployed successfully!'}, 200

        except Exception as e:
            return {'error': str(e)}, 500

    def reformat_port(self, container_port_str: Union[str, None]) -> Union[Dict[str, Any], None]:
        """Reformat the port information from the container info."""
        if container_port_str is None:
            return None  # If no port is provided, return None
        try:
            temp_dict = ast.literal_eval(container_port_str)
            port_mapping = {f"{int(key.split('/')[0])}/tcp": value for key, value in temp_dict.items()}
            return port_mapping

        except Exception as e:
            raise ValueError(f"Error parsing port mapping: {e}")
