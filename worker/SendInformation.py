import requests
import uuid
import psutil, multiprocessing
import argparse

class SendInformation:
    def __init__(self):
        self.args = self.get_arguments()

    def post(self, url: str, data: dict) -> requests.Response:
        return requests.post(url, json=data)

    def register(self) -> None:
        data = {
            "id": str(uuid.uuid4()),
            "ip": self.args.worker_ip,
            "ram": psutil.virtual_memory().total,
            "cpu": multiprocessing.cpu_count(),
            "status": "RUNNING",
        }

        result = self.post(f"{self.args.master_ip}/worker", data)
        if result.status_code == 200:
            print("Worker registered successfully")
        else:
            print(result.text)
            raise Exception(f"Worker registration failed {result.status_code}")

    def get_arguments(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser()
        parser.add_argument("-m", "--master-ip", help="Master URL")
        parser.add_argument("-i", "--worker-ip", help="Worker IP")
        return parser.parse_args()

    def main(self):
        self.register()

if __name__ == "__main__":
    SendInformation().main()
