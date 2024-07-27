import psutil
import socket
import requests
import time
import threading
import argparse
import logging
import os

from worker.conf.logging_config import setup_logging

class InfoSender:
    def __init__(self, worker_id: str, args: argparse.Namespace, stop_event: threading.Event) -> None:
        self.worker_id = worker_id  # Initialize with uuid
        self.args = args  # Store command-line arguments
        self.log_file = f'logs/info_sender_{worker_id}.log'
        setup_logging(self.log_file)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info('InfoSender initialized')
        self.stop_event = stop_event  # Event to signal the thread to stop

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

    def delete(self, url: str) -> requests.Response:
        """Perform a DELETE request."""
        try:
            response = requests.delete(url)
            response.raise_for_status()
            self.logger.info(f"DELETE request to {url} successful")
            return response

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error during DELETE request to {url}: {e}")
            raise

    def get_worker_data(self) -> dict:
        """Prepare worker data for transmission."""
        data = {
            "ip": socket.gethostbyname(socket.gethostname()),
            "ram-usage": psutil.virtual_memory().percent,
            "cpu-usage": psutil.cpu_percent(interval=1),
            "status": "ACTIVE",
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
        while not self.stop_event.is_set():
            data = self.get_worker_data()

            try:
                result = self.put(f"{self.args.master_ip}/worker/{self.worker_id}", data)
                self.logger.info(f"Worker {eval(result.text)["id"]} has successfully updated")

            except requests.exceptions.RequestException as e:
                self.logger.error(f"Worker update failed: {e}")
                if "Name or service not known" in str(e):
                    self.logger.warning("Master server not found. Please check the master IP address.")
                raise

            self.stop_event.wait(5)  # Sleep for 5 seconds or until the event is set

    def delete_info(self) -> None:
        """Delete worker information when stopping."""
        try:
            result = self.delete(f"{self.args.master_ip}/worker/{self.worker_id}")
            self.logger.info(f"Worker {self.worker_id} has successfully deleted")

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Worker deletion failed: {e} and result: {result.text}")
            if "Name or service not known" in str(e):
                self.logger.warning("Master server not found. Please check the master IP address.")
            raise

    def main(self) -> None:
        """Main execution function."""
        try:
            self.register()

            # Create a thread for the update_info loop
            self.update_thread = threading.Thread(target=self.update_info)
            self.update_thread.start()  # Start the update thread

        except Exception as e:
            self.logger.error(f"An error occurred in main: {e}")

    def stop(self) -> None:
        """Stop the InfoSender thread."""
        self.stop_event.set()  # Signal the thread to stop
        self.update_thread.join()  # Wait for the thread to finish
        self.delete_info()  # Delete worker information when stopping
