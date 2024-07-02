from master.database.Repository import Repository
from master.WorkersList import WorkersList
from master.WorkerInfo import WorkerInfo

class WorkerSelector:
    def __init__(self, repository: Repository) -> None:
        self.repository = repository
        self.workers_list = WorkersList(repository)
        self.worker_info = WorkerInfo(repository)

    def select_worker(self) -> dict:
        """Select a worker from the database with the least RAM and CPU usage and return its details."""
        
        workers, status = self.workers_list.get()
        if not workers:
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

        return best_worker

    def get_worker_url(self) -> str:
        """Construct and return the URL for a randomly selected worker."""
        worker, status = self.worker_info.get(self.select_worker())
        if 'ip' not in worker:
            raise KeyError("Selected worker data does not contain an 'ip' field.")
        return f"http://{worker['ip']}:18081"
    
    def main(self) -> str:
        return self.get_worker_url()
