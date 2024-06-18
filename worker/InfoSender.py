import psutil
import socket
import requests
import time
import threading, argparse

class InfoSender:
    def __init__(self, worker_id: str, args: argparse.Namespace) -> None:
        self.worker_id = worker_id  # Initialize with uuid
        self.args = args  # Store command-line arguments

    def post(self, url: str, data: dict) -> requests.Response:
        """Perform a POST request."""
        return requests.post(url, json=data)

    def put(self, url: str, data: dict) -> requests.Response:
        """Perform a PUT request."""
        return requests.put(url, json=data)

    def get_worker_data(self) -> dict:
        """Prepare worker data for transmission."""
        return {
            "ip": socket.gethostbyname(socket.gethostname()),
            "ram-usage": psutil.virtual_memory().percent,
            "cpu-usage": psutil.cpu_percent(interval=1),
            "status": "RUNNING",
        }

    def register(self) -> None:
        """Register worker with master server."""
        data = self.get_worker_data()
        data["id"] = self.worker_id

        result = self.post(f"{self.args.master_ip}/worker", data)
        if result.status_code == 200:
            print("Worker registered successfully")
        else:
            print(result.text)
            raise Exception(f"Worker registration failed {result.status_code}")

        time.sleep(5)

    def update_info(self) -> None:
        """Update worker information periodically."""
        while True:
            data = self.get_worker_data()

            result = self.put(f"{self.args.master_ip}/worker/{self.worker_id}", data)
            if result.status_code == 200:
                print("Worker updated successfully")
            else:
                print(result.text)
                raise Exception(f"Worker update failed {result.status_code}")

            time.sleep(5)

    def main(self) -> None:
        """Main execution function."""
        self.register()

        # Create a thread for the update_info loop
        update_thread = threading.Thread(target=self.update_info)
        update_thread.start() # Start the update thread

        # Wait for the update thread to complete
        update_thread.join()
