import requests
import random
from master.cli import get_arguments
from master.database.Repository import Repository
from master.database.RedisDB import Redis
from master.conf.config import CONFIG

class ImageSender:
    def __init__(self, repository:Repository) -> None:
        self.args = get_arguments()
        self.db = repository
        self.port = CONFIG.get('routes', {}).get('worker', {}).get('port')
        self.pull_path = CONFIG.get('routes', {}).get('worker', {}).get('pull')


    def post(self, url: str, data: str) -> requests.Response:
        return requests.post(url, json=data)

    def find_worker(self) -> str:
        print(self.db.read(random.choice(self.db.read_all())))
        return f"http://{self.db.read(random.choice(self.db.read_all()))['ip']}:{self.port}"

    def send_image(self, worker_url: str) -> None:
        data = self.args.image_name
        result = self.post(f"{worker_url}{self.pull_path}", data)

        if result.status_code == 200:
            print("Successfully pulled image")
        else:
            print(result.text)
            raise Exception(f"Failed to pull image: {data}. {result.status_code}")

    def main(self)-> None:
        self.send_image(self.find_worker())

if __name__ == "__main__":
    ImageSender(repository=Redis()).main()
