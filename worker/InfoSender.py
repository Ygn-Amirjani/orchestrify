import psutil
import socket
import requests
import time
import threading, argparse
import logging

from worker.conf.logging_config import setup_logging

class InfoSender:
    def __init__(self, worker_id: str, args: argparse.Namespace) -> None:
        self.worker_id = worker_id  # Initialize with uuid
        self.args = args  # Store command-line arguments
        log_file = f'logs/info_sender_{worker_id}.log'
        setup_logging(log_file)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info('InfoSender initialized')

    def post(self, url: str, data: dict) -> requests.Response:
        """Perform a POST request."""
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            self.logger.info(f"POST request to {url} successful")
            return response

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error during POST request to {url}: {e}")
            raise

    def put(self, url: str, data: dict) -> requests.Response:
        """Perform a PUT request."""
        try:
            response = requests.put(url, json=data)
            response.raise_for_status()
            self.logger.info(f"PUT request to {url} successful")
            return response

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error during PUT request to {url}: {e}")
            raise

    def get_worker_data(self) -> dict:
        """Prepare worker data for transmission."""
        data = {
            "ip": socket.gethostbyname(socket.gethostname()),
            "ram-usage": psutil.virtual_memory().percent,
            "cpu-usage": psutil.cpu_percent(interval=1),
            "status": "RUNNING",
        }
        self.logger.debug(f"Worker data: {data}")
        return data
        
    def register(self) -> None:
        """Register worker with master server."""
        data = self.get_worker_data()
        data["id"] = self.worker_id

        try:
            result = self.post(f"{self.args.master_ip}/worker", data)
            self.logger.info(f"Worker {eval(result.text)["id"]} has successfully registered")

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Worker registration failed: {e}")
            if "Connection refused" in str(e):
                self.logger.warning("Master server not found. Please check the master IP address.")
            raise

        time.sleep(5)

    def update_info(self) -> None:
        """Update worker information periodically."""
        while True:
            data = self.get_worker_data()

            try:
                result = self.put(f"{self.args.master_ip}/worker/{self.worker_id}", data)
                self.logger.info(f"Worker {eval(result.text)["id"]} has successfully updated")

            except requests.exceptions.RequestException as e:
                self.logger.error(f"Worker update failed: {e}")
                if "Name or service not known" in str(e):
                    self.logger.warning("Master server not found. Please check the master IP address.")
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
            self.logger.error(f"An error occurred in main: {e}")
