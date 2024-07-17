from flask_restful import Resource
from typing import Tuple, List
from master.database.Repository import Repository
from master.conf.logging_config import setup_logging

import logging

class ContainersList(Resource):
    def __init__(self, repository: Repository) -> None:
        self.repository = repository
        log_file = "logs/master_app.log"
        setup_logging(log_file)
        self.logger = logging.getLogger(self.__class__.__name__)

    def get(self) -> Tuple[List[str], int]:
        """List of all Containers."""
        try:
            all_keys = self.repository.read_all()
            container_keys = [key for key in all_keys if key.startswith("container:")]

            self.logger.info("Retrieved list of all containers.")
            return container_keys, 200

        except Exception as e:
            self.logger.error(f"Failed to retrieve container list: {str(e)}")
            return {"error": f"Internal Server Error: {str(e)}"}, 500
