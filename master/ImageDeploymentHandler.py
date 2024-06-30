import requests
import argparse
from master.database.Repository import Repository

class ImageDeploymentHandler:
    def __init__(self, repository: Repository, args: argparse.Namespace) -> None:
        self.repository = repository
        self.args = args    # Store command-line arguments

    def post(self, url: str, data: str) -> requests.Response:
        """Perform a POST request."""
        return requests.post(url, json=data)

    def select_worker(self) -> dict:
        """Select a worker from the database with the least RAM and CPU usage and return its details."""
        all_keys = self.repository.read_all()
        workers = [key for key in all_keys 
                if key.startswith("worker:") and key.endswith("status")]

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
        worker = self.repository.read(self.select_worker())
        if 'ip' not in worker:
            raise KeyError("Selected worker data does not contain an 'ip' field.")
        return f"http://{worker['ip']}:18081"

    def send_image(self, worker_url: str) -> None:
        """Send the image to the worker for pulling."""
        data = self.args.image_name
        result = self.post(f"{worker_url}/pull_image", data)

        if result.status_code == 200:
            print("Successfully pulled image")
        else:
            print(result.text)
            raise Exception(f"Failed to pull image: {data}. {result.status_code}")

    def run_image(self, worker_url: str) -> dict:
        """Run the image on the worker."""
        data = {
            "image_name": self.args.image_name,
            "name": self.args.name,
            "network_mode": self.args.network,
            "port": self.args.port,
            "environment": self.args.environment
        }

        # Remove keys with None values
        data = {k: v for k, v in data.items() if v is not None}

        # Run container on best worker
        result = self.post(f"{worker_url}/run_image", data)

        if result.status_code == 200:
            print("Successfully ran image")

            # Extract and save worker IP
            data["worker_ip"] = worker_url.split("//")[1].split(":")[0]
            data.update({"id": result.json().get("container_id")})
            return data
        else:
            print(result.text)
            raise Exception(f"Failed to run image: {data}. {result.status_code}")

    def save_container_info(self, container_info: dict) -> None:
        """Save the container information to the repository."""
        if container_info.get('port'):
            host_port = next(iter(container_info['port'].values()))
            container_info['port'] = host_port 

        self.repository.create(f"container:{container_info['id']}:status", container_info)

    def main(self) -> None:
        """Main method to manage the deployment process."""
        worker_url = self.get_worker_url()
        self.send_image(worker_url)
        container_info = self.run_image(worker_url)
        self.save_container_info(container_info)

        if container_info.get('port'):
            print (f'"container_url" => {container_info["worker_ip"]}:{container_info["port"]}')
