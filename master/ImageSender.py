import requests
import random
from master.database.Repository import Repository

class ImageSender:
    def __init__(self, repository:Repository, args: str, port: str, path: str) -> None:
        self.args = args
        self.db = repository
        self.port = port
        self.path = path

    def post(self, url: str, data: str) -> requests.Response:
        return requests.post(url, json=data)

    def find_worker(self) -> str:
        return f"http://{self.db.read(random.choice(self.db.read_all()))['ip']}:{self.port}"

    def send_image(self, worker_url: str) -> None:
        data = self.args.image_name
        result = self.post(f"{worker_url}{self.path}", data)

        if result.status_code == 200:
            print("Successfully pulled image")
        else:
            print(result.text)
            raise Exception(f"Failed to pull image: {data}. {result.status_code}")

    def main(self)-> None:
        self.send_image(self.find_worker())
