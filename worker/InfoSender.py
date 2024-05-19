from cli import get_arguments
import psutil, multiprocessing
import requests
import uuid

class InfoSender:
    def __init__(self) -> None:
        self.args = get_arguments()

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

    def main(self) -> None:
        self.register()

if __name__ == "__main__":
    InfoSender().main()
