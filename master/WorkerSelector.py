from master.database.Repository import Repository
from master.WorkersList import WorkersList
from master.WorkerInfo import WorkerInfo
from master.conf.logging_config import setup_logging

import logging

class WorkerSelector:
    def __init__(self, repository: Repository, workers: list) -> None:
        self.repository = repository
        self.workers = workers
        self.worker_info = WorkerInfo(repository)
        log_file = f'logs/image_deployment.log'
        setup_logging(log_file)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info('Worker Selector initialized')

    def select_worker(self, workers: list) -> dict:
        """Select a worker from the database with the least RAM and CPU usage and return its details."""
        try:
            if not workers :
                self.logger.error("No workers available in the database.")
                raise ValueError("No workers available in the database.")

            best_worker = None
            min_resources_usage = float('inf')

            for worker_key in workers:
                worker = self.repository.read(worker_key)
                ram_usage = worker.get('ram-usage', float('inf'))
                cpu_usage = worker.get('cpu-usage', float('inf'))
                status = worker.get('status', 'unknown')

                # Only consider workers that are in 'running' status
                if status != "RUNNING":
                    self.logger.info(f"Skipping worker {worker_key} with status {status}")
                    continue

                total_usage = float(ram_usage + cpu_usage)
                if total_usage < min_resources_usage:
                    min_resources_usage = total_usage
                    best_worker = worker_key

            if best_worker is None:
                self.logger.error("No suitable worker found based on RAM and CPU usage.")
                raise ValueError("No suitable worker found based on RAM and CPU usage.")

            self.logger.info(f"Selected worker: {best_worker}")
            return best_worker.split(':')[1]

        except Exception as e:
            self.logger.error(f"Error selecting worker: {e}")
            raise RuntimeError(f"Error selecting worker: {e}")

    def get_worker_url(self, selected_worker: dict) -> str:
        """Construct and return the URL for a randomly selected worker."""
        try:
            worker, status = self.worker_info.get(selected_worker)
            if 'ip' not in worker:
                self.logger.error("Selected worker data does not contain an 'ip' field.")
                raise KeyError("Selected worker data does not contain an 'ip' field.")
            url = f"http://{worker['ip']}:18081"
            self.logger.info(f"Constructed URL for worker: {url}")
            return url


        except KeyError as ke:
            self.logger.error(f"Error getting worker URL: {ke}")
            raise RuntimeError(f"Error getting worker URL: {ke}")

        except Exception as e:
            self.logger.error(f"Error getting worker URL: {e}")
            raise RuntimeError(f"Error getting worker URL: {e}")

    def main(self) -> str:
        try:
            selected_worker = self.select_worker(self.workers)
            worker_url = self.get_worker_url(selected_worker)
            self.logger.info(f"Worker URL: {worker_url}")
            return worker_url

        except Exception as e:
            self.logger.error(f"Exception in main: {e}")
            return f"Error: {e}"
