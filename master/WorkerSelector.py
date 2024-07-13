from master.database.Repository import Repository
from master.WorkersList import WorkersList
from master.WorkerInfo import WorkerInfo

class WorkerSelector:
    def __init__(self, repository: Repository, workers: list) -> None:
        self.repository = repository
        self.workers = workers
        self.worker_info = WorkerInfo(repository)

    def select_worker(self, workers: list) -> dict:
        """Select a worker from the database with the least RAM and CPU usage and return its details."""
        try:
            if not workers :
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
                    continue

                total_usage = float(ram_usage + cpu_usage)
                if total_usage < min_resources_usage:
                    min_resources_usage = total_usage
                    best_worker = worker_key

            if best_worker is None:
                raise ValueError("No suitable worker found based on RAM and CPU usage.")

            return best_worker.split(':')[1]

        except Exception as e:
            raise RuntimeError(f"Error selecting worker: {e}")

    def get_worker_url(self, selected_worker: dict) -> str:
        """Construct and return the URL for a randomly selected worker."""
        try:
            worker, status = self.worker_info.get(selected_worker)
            if 'ip' not in worker:
                raise KeyError("Selected worker data does not contain an 'ip' field.")
            return f"http://{worker['ip']}:18081"

        except KeyError as ke:
            raise RuntimeError(f"Error getting worker URL: {ke}")

        except Exception as e:
            raise RuntimeError(f"Error getting worker URL: {e}")

    def main(self) -> str:
        try:
            selected_worker = self.select_worker(self.workers)
            worker_url = self.get_worker_url(selected_worker)
            return worker_url

        except Exception as e:
            return f"Error: {e}"
