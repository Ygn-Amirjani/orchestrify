import requests
import random

from cli import get_arguments
from database.Repository import Repository
from database.RedisDB import Redis

class ImageSender:
    def __init__(self, repository:Repository) -> None:
        self.args = get_arguments()
        self.db = repository

    def post(self, url: str, data: str) -> requests.Response:
        return requests.post(url, json=data)

    def find_worker(self) -> str:
        print(self.db.read(random.choice(self.db.read_all())))
        return f"http://{self.db.read(random.choice(self.db.read_all()))['ip']}:18081"

    def send_image(self, worker_url: str) -> None:
        data = self.args.image_name
        result = self.post(f"{worker_url}/pull_image", data)

        if result.status_code == 200:
            print("Successfully pulled image")
        else:
            print(result.text)
            raise Exception(f"Failed to pull image: {data}. {result.status_code}")

    def main(self)-> None:
        self.send_image(self.find_worker())

if __name__ == "__main__":
    ImageSender(repository=Redis()).main()
