from flask_restful import Resource
from worker.conf.logging_config import setup_logging

import logging
import os

class LoggerFileDeleter(Resource):
    def __init__(self) -> None:
        log_file = "logs/worker_app.log"
        setup_logging(log_file)
        self.logger = logging.getLogger(self.__class__.__name__)

    def get(self, file):
        try:
            file_path = f"logs/{file}"
            if os.path.exists(file_path):
                os.remove(file_path)
                message = f"Log file {file_path} deleted"
                self.logger.info(message)
                return {"status": "ok", "message": message}, 200
            else:
                message = f"Log file {file_path} does not exist"
                self.logger.error(message)
                return {"status": "error", "message": message}, 404
        except Exception as e:
            self.logger.error(f"Error deleting log file: {str(e)}")
            return {"status": "error", "message": f"Error deleting log file: {str(e)}"}, 500
