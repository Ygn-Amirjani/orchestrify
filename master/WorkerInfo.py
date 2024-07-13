from flask_restful import Resource
from typing import Tuple, Dict, Any
from master.database.Repository import Repository
from master.WorkersList import WorkersList

class WorkerInfo(Resource):
    def __init__(self, repository: Repository) -> None:
        self.repository = repository
        self.workers_list = WorkersList(repository)

    def get(self, worker_id: str) -> Tuple[Dict[str, Any], int]:
        """Retrieve information of the requested worker."""
        try:
            worker_keys, status = self.workers_list.get()

            for worker_key in worker_keys:
                if worker_id == worker_key.split(':')[1]:
                    worker_info = self.repository.read(worker_key)
                    if worker_info:
                        return worker_info, 200
                    else:
                        return {"error": "Worker information not found in the database."}, 404

            return {"error": f"Worker with ID '{worker_id}' not found."}, 404

        except KeyError as ke:
            return {"error": f"KeyError: {str(ke)}"}, 400

        except ValueError as ve:
            return {"error": f"ValueError: {str(ve)}"}, 400

        except Exception as e:
            return {"error": f"Internal Server Error: {str(e)}"}, 500
