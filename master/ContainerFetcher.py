from flask_restful import Resource
from flask import request
from typing import List, Dict, Tuple, Any, Union
import logging

from master.database.Repository import Repository
from master.ContainersList import ContainersList
from master.conf.logging_config import setup_logging

class ContainerFetcher(Resource):
    def __init__(self, repository: Repository) -> None:
        self.repository = repository
        self.containers_list = ContainersList(repository)
        self.container_port: Union[str, None] = None
        self.ips: List[str] = []

        # Set up logging
        log_file = f'logs/proxy.log'
        setup_logging(log_file)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info('ContainerFetcher initialized')

    def post(self) -> Tuple[Dict[str, Union[str, List[str]]], int]:
        """Handle POST requests to fetch container information."""
        try:
            data = request.get_json()
            self.logger.debug(f"Received request data: {data}")

            if not data :
                self.logger.error("No data provided in request")
                return {"status": "error",
                        "message": "Container name is required in data."
                }, 400
            
            self.logger.info(f"Fetching containers for name: {data}")
            container_keys, status = self.containers_list.get()

            found_container = False
            for container_key in container_keys:
                if container_key.split(":")[1] != data:
                    continue

                container_info = self.repository.read(container_key)
                self.logger.debug(f"Container info: {container_info}")
                self.container_port = container_info.get('port').split(': ')[1].strip('}')
                self.ips.append(container_info.get("worker_ip"))
                found_container = True

            if not found_container:
                self.logger.warning(f"Container with name '{data}' not found")
                return {
                    "status": "error",
                    "message": f"Container with name '{data}' not found."
                }, 404

            response = {
                "status": "ok",
                "port": self.container_port, "ips": self.ips
            }, 200
            self.logger.info(f"Returning response: {response}")
            return response

        except KeyError as ke:
            self.logger.error(f"KeyError: {str(ke)}")
            return {"status": "error", "message": f"KeyError: {str(ke)}"}, 400

        except ValueError as ve:
            self.logger.error(f"ValueError: {str(ve)}")
            return {"status": "error", "message": f"ValueError: {str(ve)}"}, 400

        except Exception as e:
            self.logger.error(f"Internal Server Error: {str(e)}")
            return {"status": "error", "message": f"Internal Server Error: {str(e)}"}, 500
