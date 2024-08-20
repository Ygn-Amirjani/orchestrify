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
    def __init__(self, repository: Repository, master_ip: str) -> None:
        self.repository = repository
        self.master_ip = master_ip
        self.workers_list = WorkersList(repository)
        self.log_file = "logs/master_app.log"
        setup_logging(self.log_file)
        self.logger = logging.getLogger(self.__class__.__name__)

    def delete(self, worker_id: str) -> Tuple[Dict[str, Any], int]:
        try:
            worker_keys, status = self.workers_list.get()
            for worker_key in worker_keys:
                if worker_id == worker_key.split(':')[1]:
                    return self._delete_worker(worker_key, worker_id)

            self.logger.warning(f"Worker with ID '{worker_id}' not found.")
            return {"error": f"Worker with ID '{worker_id}' not found."}, 404

        except KeyError as ke:
            self.logger.error(f"KeyError: {str(ke)}")
            return {"error": f"KeyError: {str(ke)}"}, 400

        except ValueError as ve:
            self.logger.error(f"ValueError: {str(ve)}")
            return {"error": f"ValueError: {str(ve)}"}, 400

        except Exception as e:
            self.logger.error(f"Internal Server Error: {str(e)}", exc_info=True)
            return {"error": f"Internal Server Error: {str(e)}"}, 500

    def _delete_worker(self, worker_key: str, worker_id: str) -> Tuple[Dict[str, Any], int]:
        worker_info = self.repository.read(worker_key)
        if not worker_info:
            self.logger.warning(f"Worker with ID '{worker_id}' not found.")
            return {"error": "Worker information not found in the database."}, 404

        self.repository.delete(worker_key)

        worker_info['status'] = 'INACTIVE'
        self._notify_reallocator(worker_info)

        self._delete_remote_log(worker_info, worker_id)
        self._delete_local_log(worker_id)
        self.logger.info(f"Successfully retrieved and deleted worker {worker_id}")
        return worker_info, 200

    def _notify_reallocator(self, worker_key: str) -> None:
        try:
            response = requests.post(f'http://{self.master_ip}:18080/reallocator', json=worker_key)
            if response.status_code == 200:
                self.logger.info(f"Successfully notified reallocator for worker {worker_key}")
            else:
                self.logger.error(f"Failed to notify reallocator for worker {worker_key}: {response.content}")
        except requests.RequestException as re:
            self.logger.error(f"RequestException while notifying reallocator for worker {worker_key}: {str(re)}")

    def _delete_remote_log(self, worker_info: Dict[str, Any], worker_id: str) -> None:
        logger_file = f"info_sender_{worker_id}.log"
        key = f"http://{worker_info.get('ip')}:18081/del/{logger_file}"
        try:
            response = requests.get(key)
            if response.status_code == 200:
                self.logger.info(f"Successfully deleted log file for worker {worker_id} on IP {worker_info.get('ip')}")
            else:
                self.logger.error(f"Failed to delete log file for worker {worker_id} on IP {worker_info.get('ip')}: {response.content}")
        except requests.RequestException as re:
            self.logger.error(f"RequestException while trying to delete log file for worker {worker_id} on IP {worker_info.get('ip')}: {str(re)}")

    def _delete_local_log(self, worker_id: str) -> None:
        log_file = f"logs/worker_register_{worker_id}.log"
        if os.path.exists(log_file):
            time.sleep(5)  # Ensure file is not in use
            os.remove(log_file)
            self.logger.info(f"Log file {log_file} deleted")
        else:
            self.logger.warning(f"Log file {log_file} not found for deletion")
