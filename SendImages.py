import requests
import argparse
import random

from Redis import Redis

class SendImages:
    def __init__(self) -> None:
        self.args = self.get_arguments()

    def post(self, url: str, data: str) -> requests.Response:
        return requests.post(url, json=data)

    def find_worker(self):
        redis = Redis()
        print(redis.read(random.choice(redis.read_all())))
        return f"http://{redis.read(random.choice(redis.read_all()))['ip']}:18081"

    def send_image(self, worker_url: str) -> None:
        data = self.args.image_name
        result = self.post(f"{worker_url}/pull_image", data)

        if result.status_code == 200:
            print("Successfully pulled image")
        else:
            print(result.text)
            raise Exception(f"Failed to pull image: {data}. {result.status_code}")

    def get_arguments(self) -> argparse.Namespace:
        """Get arguments from CLI using argparse"""
        parser = argparse.ArgumentParser()
        parser.add_argument("-i", "--image-name", help="Image NAME")
        return parser.parse_args()

    def main(self):
        self.send_image(self.find_worker())

if __name__ == "__main__":
    SendImages().main()
