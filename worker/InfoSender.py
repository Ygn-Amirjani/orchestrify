from cli import get_arguments
import psutil , socket
import requests
import uuid, time

class InfoSender:
    def __init__(self) -> None:
        self.args = get_arguments()
        self.worker_id = str(uuid.uuid4())

    def post(self, url: str, data: dict) -> requests.Response:
        return requests.post(url, json=data)

    def put(self, url: str, data: dict) -> requests.Response:
        return requests.put(url, json=data)

    def get_worker_data(self) -> dict:
        """Prepare the worker data to be sent to the master"""
        return {
            "ip": self.args.worker_ip,
            "ram": psutil.virtual_memory().percent,
            "cpu": psutil.cpu_percent(interval=1),
            "status": "RUNNING",
        }

    def register(self) -> None:
        data = self.get_worker_data()
        data["id"] = self.worker_id

        result = self.post(f"{self.args.master_ip}/worker", data)
        if result.status_code == 200:
            print("Worker registered successfully")
        else:
            print(result.text)
            raise Exception(f"Worker registration failed {result.status_code}")

    def update_info(self):
        data = self.get_worker_data()

        result = self.put(f"{self.args.master_ip}/worker/{self.worker_id}", data)
        if result.status_code == 200:
            print("Worker updated successfully")
        else:
            print(result.text)
            raise Exception(f"Worker update failed {result.status_code}")

    def main(self) -> None:
        self.register()
        time.sleep(15)
        while True:
            self.update_info()
            time.sleep(15)

if __name__ == "__main__":
    InfoSender().main()
