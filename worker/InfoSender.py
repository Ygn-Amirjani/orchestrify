# InfoSender.py
import psutil
import socket
import requests
import time
import threading, argparse
from worker.conf.config import CONFIG

class InfoSender:
    def __init__(self, worker_id: str, args: argparse.Namespace, path: str) -> None:
        self.worker_id = worker_id
        self.args = args
        self.path = path

    def post(self, url: str, data: dict) -> requests.Response:
        return requests.post(url, json=data)

    def put(self, url: str, data: dict) -> requests.Response:
        return requests.put(url, json=data)

    def get_worker_data(self) -> dict:
        """Prepare the worker data to be sent to the master"""
        return {
            "ip": socket.gethostbyname(socket.gethostname()),
            "ram": psutil.virtual_memory().percent,
            "cpu": psutil.cpu_percent(interval=1),
            "status": "RUNNING",
        }

    def register(self) -> None:
        data = self.get_worker_data()
        data["id"] = self.worker_id

        result = self.post(f"{self.args.master_ip}{self.path}", data)
        if result.status_code == 200:
            print("Worker registered successfully")
        else:
            print(result.text)
            raise Exception(f"Worker registration failed {result.status_code}")
        
        time.sleep(5)

    def update_info(self):
        while True:
            data = self.get_worker_data()

            result = self.put(f"{self.args.master_ip}{self.path}/{self.worker_id}", data)
            if result.status_code == 200:
                print("Worker updated successfully")
            else:
                print(result.text)
                raise Exception(f"Worker update failed {result.status_code}")

            time.sleep(5)

    def main(self) -> None:
        self.register()
        # Create a thread for the update_info loop
        update_thread = threading.Thread(target=self.update_info)
        update_thread.start()
        # Wait for thread to complete
        update_thread.join()
