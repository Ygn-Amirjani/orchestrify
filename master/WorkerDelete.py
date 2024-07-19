from flask_restful import Resource
from typing import Tuple, Dict, Any
from master.database.Repository import Repository
from master.WorkersList import WorkersList
from master.conf.logging_config import setup_logging

import logging
import os

class WorkerDelete(Resource):
    def __init__(self, repository: Repository) -> None:
        self.repository = repository
        self.workers_list = WorkersList(repository)
        self.log_file = "logs/master_app.log"
        setup_logging(self.log_file)
        self.logger = logging.getLogger(self.__class__.__name__)

    def delete(self, worker_id: str) -> Tuple[Dict[str, Any], int]:
        try:

            worker_keys, status = self.workers_list.get()
            for worker_key in worker_keys:
                if worker_id == worker_key.split(':')[1]:
                    worker_info = self.repository.read(worker_key)
                    self.repository.delete(worker_key)
                    if worker_info:
                        self.logger.info(f"Successfully retrieved info for worker {worker_id}")

                        # Remove the log file
                        log_file = f"logs/worker_register_{worker_id}.log"
                        if os.path.exists(log_file):
                            os.remove(log_file)
                            self.logger.info(f"Log file {log_file} deleted")

                        return worker_info, 200

                    else:
                        self.logger.warning(f"Worker with ID '{worker_id}' not found.")
                        return {"error": "Worker information not found in the database."}, 404
                
            self.logger.warning(f"Worker with ID '{worker_id}' not found.")
            return {"error": f"Worker with ID '{worker_id}' not found."}, 404

        except KeyError as ke:
            self.logger.error(f"KeyError: {str(ke)}")
            return {"error": f"KeyError: {str(ke)}"}, 400

        except ValueError as ve:
            self.logger.error(f"ValueError: {str(ve)}")
            return {"error": f"ValueError: {str(ve)}"}, 400

        except Exception as e:
            self.logger.error(f"Internal Server Error: {str(e)}")
            return {"error": f"Internal Server Error: {str(e)}"}, 500
