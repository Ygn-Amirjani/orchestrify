from flask_restful import Resource, reqparse
from typing import Tuple, Dict, Any
from master.database.Repository import Repository
from master.conf.logging_config import setup_logging

import logging

class WorkerUpdater(Resource):
    def __init__(self, repository: Repository) -> None:
        self.repository = repository
        self.logger = logging.getLogger(self.__class__.__name__)

    def put(self, worker_id: str) -> Tuple[Dict[str, Any], int]:
        """Updating worker information in the database."""
        try:
            parser = reqparse.RequestParser()
            parser.add_argument("ip", type=str, required=True)
            parser.add_argument("ram-usage", type=int, required=True)
            parser.add_argument("cpu-usage", type=int, required=True)
            parser.add_argument("status", type=str, required=True)

            # strict=True raises 400 if any argument is missing
            args = parser.parse_args(strict=True)

            log_file = f"logs/worker_register_{worker_id}.log"
            setup_logging(log_file)
            self.logger.info('Worker Updated initialized')

            worker_status = f"worker:{worker_id}:{args['ip']}"
            worker_data = self.repository.read(worker_status)
            if not worker_data:
                return {"message": "Worker not found"}, 404

            self.repository.update(worker_status, args)

            self.logger.info(f"Worker {worker_id} updated successfully")
            return {"status": "ok", "id": worker_id}, 200

        except ValueError as e:
            self.logger.error(f"Invalid input: {e}")
            return {"message": f"Invalid input: {e}"}, 400

        except KeyError as e:
            self.logger.error(f"Missing key in input: {e}")
            return {"message": f"Missing key in input: {e}"}, 400

        except Exception as e:
            self.logger.exception(f"Internal server error: {e}")
            return {"message": f"Internal server error: {e}"}, 500
