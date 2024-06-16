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

    def find_worker(self) -> str:
        return f"http://{self.db.read(random.choice(self.db.read_all()))['ip']}:{self.port}"

    def send_image(self, worker_url: str) -> None:
        data = self.args.image_name
        result = self.post(f"{worker_url}{self.pull_path}", data)

        if result.status_code == 200:
            print("Successfully pulled image")
        else:
            print(result.text)
            raise Exception(f"Failed to pull image: {data}. {result.status_code}")

    def run_image(self, worker_url: str) -> None:
        data = self.args.image_name
        result = self.post(f"{worker_url}{self.run_path}", data)

        if result.status_code == 200:
            print("Successfully ran image")
        else:
            print(result.text)
            raise Exception(f"Failed to run image: {data}. {result.status_code}")

    def main(self) -> None:
        worker_url = self.find_worker()
        self.send_image(worker_url)
        self.run_image(worker_url)
