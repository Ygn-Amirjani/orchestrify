import requests
import random
from master.database.Repository import Repository

class ImageDeploymentHandler:
    def __init__(self, repository: Repository, args: str, 
                port: str,pull_path: str, run_path: str) -> None:
        self.args = args
        self.db = repository
        self.port = port
        self.pull_path = pull_path
        self.run_path = run_path

    def post(self, url: str, data: str) -> requests.Response:
        return requests.post(url, json=data)

    def select_worker(self) -> dict:
        """Selects a random worker from the database and returns its details."""
        all_keys = self.db.read_all()
        workers = [key for key in all_keys
            if key.startswith("worker:") and key.endswith("status")]
        if not workers:
            raise ValueError("No workers available in the database.")
        return random.choice(workers)

    def get_worker_url(self) -> str:
        """Constructs and returns the URL for a randomly selected worker."""
        worker = self.db.read(self.select_worker())
        if 'ip' not in worker:
            raise KeyError("Selected worker data does not contain an 'ip' field.")
        return f"http://{worker['ip']}:{self.port}"

    def send_image(self, worker_url: str) -> None:
        data = self.args.image_name
        result = self.post(f"{worker_url}{self.pull_path}", data)

        if result.status_code == 200:
            print("Successfully pulled image")
        else:
            print(result.text)
            raise Exception(f"Failed to pull image: {data}. {result.status_code}")

    def run_image(self, worker_url: str) -> str:
        data = self.args.image_name
        result = self.post(f"{worker_url}{self.run_path}", data)

        if result.status_code == 200:
            print("Successfully ran image")
            return result.json().get("container_id")
        else:
            print(result.text)
            raise Exception(f"Failed to run image: {data}. {result.status_code}")

    def save_container_info(self, container_id: str):
        worker_info = self.db.read(self.select_worker())
        container_info = {
            "Image_name": self.args.image_name,
            "Container_id": container_id,
            "Container_ip": worker_info['ip']
        }

        self.db.create(f"worker:{worker_info['id']}:container", container_info)

    def main(self) -> None:
        worker_url = self.get_worker_url()
        self.send_image(worker_url)
        container_id = self.run_image(worker_url)
        self.save_container_info(container_id)
