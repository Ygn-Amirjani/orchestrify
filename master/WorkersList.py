from flask_restful import Resource, abort
from typing import Tuple, List
from master.database.Repository import Repository
from master.conf.logging_config import setup_logging

import logging

class WorkersList(Resource):
    def __init__(self, repository: Repository) -> None:
        self.repository = repository
        log_file = "logs/master_app.log"
        setup_logging(log_file)
        self.logger = logging.getLogger(self.__class__.__name__)

    def get(self) -> Tuple[List[str], int]:
        """List of all registered workers."""
        try:
            all_keys = self.repository.read_all()
            worker_keys = [key for key in all_keys if key.startswith("worker:")]

            self.logger.info("Retrieved worker list successfully")
            return worker_keys, 200

        except Exception as e:
            self.logger(f"Failed to retrieve worker list: {str(e)}")
            return {"message": f"Failed to retrieve worker list: {e}"}, 500
