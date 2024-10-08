from flask_restful import Resource, reqparse
from typing import Tuple, Dict, Any
from master.database.Repository import Repository
from master.conf.logging_config import setup_logging
from master.WorkersList import WorkersList

import logging
import requests

class WorkerRegistrer(Resource):
    def __init__(self, repository: Repository) -> None:
        self.repository = repository
        self.workers_list = WorkersList(repository)
        self.logger = logging.getLogger(self.__class__.__name__)

    def post(self) -> Tuple[Dict[str, Any], int]:
        """Saving worker information on the database"""
        try:
            parser = reqparse.RequestParser()
            parser.add_argument("id", type=str, required=True)
            parser.add_argument("ip", type=str, required=True)
            parser.add_argument("ram-usage", type=int, required=True)
            parser.add_argument("cpu-usage", type=int, required=True)
            parser.add_argument("status", type=str, required=True)

            # strict=True raises 400 if any argument is missing
            args = parser.parse_args(strict=True)

            worker_keys, status = self.workers_list.get()
            for worker_key in worker_keys:
                if worker_key.split(":")[2] == args["ip"]:
                    worker_info = self.repository.read(worker_key)

                    try:
                        # Remove the info_sender log file
                        logger_file = f"info_sender_{args['id']}.log"
                        key = f"http://{args['ip']}:18081/del/{logger_file}"
                        response = requests.get(key)
                        if response.status_code == 200:
                            self.logger.info(f"Successfully deleted log file for worker {args['id']} on IP {args['ip']}")
                        else:
                            self.logger.error(f"Failed to delete log file for worker {args['id']}: {response.content}")

                    except requests.RequestException as re:
                        self.logger.error(f"RequestException while trying to delete log file for worker {args['id']} on IP {args['ip']}: {str(re)}")
                        return {"status": "error", "message": f"Failed to delete log file for worker {args['id']} on IP {args['ip']} due to a network error"}, 500

                    self.logger.error("This worker has already been registered and is in the database list")
                    return {"status": "error", "message": f"This IP is already used {worker_info}"}, 400

            log_file = f"logs/worker_register_{args['id']}.log"
            setup_logging(log_file)
            self.logger.info('Worker Registrer: initialized')

            self.repository.create(f"worker:{args['id']}:{args['ip']}", args)

            self.logger.info(f"Worker {args['id']} registered successfully with IP {args['ip']}")
            return {"status": "ok", "id": args["id"]}, 200

        except KeyError as ke:
            self.logger.error(f"KeyError: {str(ke)}")
            return {"status": "error", "message": f"KeyError: {str(ke)}"}, 400

        except ValueError as ve:
            self.logger.error(f"ValueError: {str(ve)}")
            return {"status": "error", "message": f"ValueError: {str(ve)}"}, 400

        except Exception as e:
            self.logger.error(f"Internal Server Error: {str(e)}")
            return {"status": "error", "message": f"Internal Server Error: {str(e)}"}, 500
