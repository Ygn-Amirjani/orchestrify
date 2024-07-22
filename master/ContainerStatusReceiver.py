import requests
import logging
import threading

from master.database.Repository import Repository
from master.ContainersList import ContainersList
from master.conf.logging_config import setup_logging

class ContainerStatusReceiver:
    def __init__(self, repository: Repository, stop_event: threading.Event) -> None:
        self.repository = repository
        self.containers_list = ContainersList(repository)
        self.log_file = 'logs/master_app.log'
        setup_logging(self.log_file)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info('ContainerStatusReceiver initialized')
        self.stop_event = stop_event  # Event to signal the thread to stop
        
    def get(self, url: str) -> requests.Response:
        """Perform a GET request."""
        try:
            response = requests.get(url)
            response.raise_for_status()
            self.logger.info(f"GET request to {url} successful")
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error during GET request to {url}: {e}")
            raise

    def receive_status(self) -> None:
        while not self.stop_event.is_set():
            container_keys, status = self.containers_list.get()
            self.logger.info(f"Fetched {len(container_keys)} container keys")
            try:
                for container_key in container_keys:
                    container_info = self.repository.read(container_key)
                    if not container_info:
                        self.logger.warning(f"No container info found for key: {container_key}")
                        continue

                    # Skip containers with statuses "Exited" or "dead"
                    if container_info.get("status") in ["Exited", "dead"]:
                        self.logger.info(f"Skipping container with key {container_key} and status {container_info.get('status')}")
                        continue
                    
                    url = f"http://{container_info.get('worker_ip')}:18081/status/{container_info.get('id')}"
                    response = self.get(url)
                    container_status = response.json().get("status")  # Assuming the response is in JSON format
                    container_info['status'] = container_status
                    self.repository.update(container_key, container_info)
                    self.logger.info(f"Received status for container {container_key}: {container_status}")
                    # Further processing of container_status as needed

            except Exception as e:
                self.logger.error(f"Failed to receive status: {e}")
                
            self.stop_event.wait(60)  # Sleep for 1 minute or until the event is set

    def main(self) -> None:
        """Main execution function."""
        try:
            # Create a thread for the receive_status loop
            self.update_thread = threading.Thread(target=self.receive_status)
            self.update_thread.daemon = True  # Set the thread as a daemon
            self.update_thread.start()  # Start the update thread

        except Exception as e:
            self.logger.error(f"An error occurred in main: {e}")

    def stop(self) -> None:
        """Stop the InfoSender thread."""
        self.stop_event.set()  # Signal the thread to stop
        self.update_thread.join()  # Wait for the thread to finish

