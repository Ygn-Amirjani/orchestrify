import requests
import argparse
from Redis import Redis
import random

def post(url: str, data: str) -> requests.Response:
    return requests.post(url, json=data)

def find_worker():
    db = Redis()
    print(db.read(random.choice(db.read_all())))
    return f"http://{db.read(random.choice(db.read_all()))['ip']}:18081"

def send_image(worker_url: str, image_name: str) -> None:
    data = image_name
    result = post(f"{worker_url}/pull_image", data)

    if result.status_code == 200:
        print("Successfully pulled image")
    else:
        print(result.text)
        raise Exception(f"Failed to pull image: {image_name}. {result.status_code}")

def get_aruments() -> argparse.Namespace:
    """Get arguments from CLI using argparse"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--image-name", help="Image NAME")
    return parser.parse_args()

def main(args: argparse.Namespace):
    send_image(find_worker(), args.image_name)

if __name__ == "__main__":
    main(get_aruments())
