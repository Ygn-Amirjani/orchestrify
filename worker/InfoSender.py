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
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response

        except requests.exceptions.RequestException as e:
            print(f"Error during POST request to {url}: {e}")
            raise

    def put(self, url: str, data: dict) -> requests.Response:
        """Perform a PUT request."""
        try:
            response = requests.put(url, json=data)
            response.raise_for_status()
            return response

        except requests.exceptions.RequestException as e:
            print(f"Error during PUT request to {url}: {e}")
            raise

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

        try:
            result = self.post(f"{self.args.master_ip}/worker", data)
            print("Worker registered successfully")

        except requests.exceptions.RequestException as e:
            print(f"Worker registration failed: {e}")
            if "Connection refused" in str(e):
                print("Master server not found. Please check the master IP address.")
            raise

        time.sleep(5)

    def update_info(self) -> None:
        """Update worker information periodically."""
        while True:
            data = self.get_worker_data()

            try:
                result = self.put(f"{self.args.master_ip}/worker/{self.worker_id}", data)
                print("Worker updated successfully")

            except requests.exceptions.RequestException as e:
                print(f"Worker update failed: {e}")
                if "Name or service not known" in str(e):
                    print("Master server not found. Please check the master IP address.")
                raise

            time.sleep(5)

    def main(self) -> None:
        """Main execution function."""
        try:
            self.register()

            # Create a thread for the update_info loop
            update_thread = threading.Thread(target=self.update_info)
            update_thread.start() # Start the update thread

            # Wait for the update thread to complete
            update_thread.join()
     
        except Exception as e:
            print(f"An error occurred in main: {e}")
