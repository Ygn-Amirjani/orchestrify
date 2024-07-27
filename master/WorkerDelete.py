from flask_restful import Resource
from typing import Tuple, Dict, Any
from master.database.Repository import Repository
from master.WorkersList import WorkersList
from master.conf.logging_config import setup_logging

import os
import time
import logging
import requests

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

                        try:
                            # Remove the info_sender log file
                            logger_file = f"info_sender_{worker_id}.log"
                            key = f"http://{worker_info.get('ip')}:18081/del/{logger_file}"
                            response = requests.get(key)
                            if response.status_code == 200:
                                self.logger.info(f"Successfully deleted log file for worker {worker_id} on IP {worker_info.get('ip')}")
                            else:
                                self.logger.error(f"Failed to delete log file for worker {worker_id} on IP {worker_info.get('ip')}: {response.content}")

                        except requests.RequestException as re:
                            self.logger.error(f"RequestException while trying to delete log file for worker {worker_id} on IP {worker_info.get('ip')}: {str(re)}")
                            return {"status": "error", "message": f"Failed to delete log file for worker {worker_id} on IP {worker_info.get('ip')} due to a network error"}, 500

                        # Remove the log file
                        log_file = f"logs/worker_register_{worker_id}.log"
                        if os.path.exists(log_file):
                            time.sleep(5)
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
