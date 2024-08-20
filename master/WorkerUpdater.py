from flask_restful import Resource, reqparse
from typing import Tuple, Dict, Any
from master.database.Repository import Repository
from master.conf.logging_config import setup_logging

import logging
import threading

class WorkerUpdater(Resource):
    def __init__(self, repository: Repository) -> None:
        self.repository = repository
        self.logger = logging.getLogger(self.__class__.__name__)
        self.worker_timers = {}
        self.lock = threading.Lock()

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
            
            # Check CPU and RAM usage to determine availability status
            if args['cpu-usage'] >= 85 or args['ram-usage'] >= 85:
                args['status'] = 'UNAVAILABLE'
            else:
                args['status'] = 'AVAILABLE'

            self.repository.update(worker_status, args)
            self.logger.info(f"Worker {worker_id} updated successfully")

            with self.lock:
                if worker_id in self.worker_timers:
                    self.worker_timers[worker_id].cancel()
                    self.logger.info(f"Previous timer for worker {worker_id} cancelled")
                timer = threading.Timer(30, self.mark_worker_inactive, [worker_id, args['ip']])
                timer.start()
                self.worker_timers[worker_id] = timer
                self.logger.info(f"New timer for worker {worker_id} with IP {args['ip']} started")

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

    def mark_worker_inactive(self, worker_id: str, ip: str) -> None:
        """Mark a worker as inactive if no updates are received."""
        with self.lock:
            worker_status = f"worker:{worker_id}:{ip}"
            worker_data = self.repository.read(worker_status)
            if worker_data:
                worker_data["status"] = "INACTIVE"
                self.repository.update(worker_status, worker_data)
                self.logger.info(f"Worker {worker_id} with IP {ip} marked as INACTIVE")
            else:
                self.logger.warning(f"Worker {worker_id} with IP {ip} was not active or not found when trying to mark as INACTIVE")
