from typing import Dict, Any
from master.conf.logging_config import setup_logging

import requests
import logging

class ContainerInfoSender:
    def __init__(self, container_name: str, master_url: str) -> None:
        self.name = container_name
        self.master_url = master_url
        log_file = "logs/loadbalancer.log"
        setup_logging(log_file)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"ContainerInfoSender initialized for container: {container_name}")

    def post(self, url: str, data: str) -> requests.Response:
        """Perform a POST request."""
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            self.logger.info(f"POST request to {url} successful")
            return response

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error during POST request to {url}: {e}")
            raise

    def send_info(self, container_name: str, url: str) -> Dict[str, Any]:
        """Send container information to the master server."""
        try:
            self.logger.info(f"Sending container information for {container_name} to master server {url}")
            result = self.post(f"{url}/container_fetcher", container_name)
            if result.status_code == 200:
                self.logger.info("Container IP sent successfully")
                data = {
                    "ip": result.json().get("ips"),
                    "port": result.json().get("port")
                }
                self.logger.debug(f"Received data: {data}")
                return data
            else:
                self.logger.error(f"Sending container IP failed with status code {result.status_code}")
                self.logger.error(result.text)
                raise Exception(f"Sending container IP failed with status code {result.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Request error: {str(e)}")
            raise

        except Exception as e:
            self.logger.error(f"Request error: {str(e)}")
            raise

    def main(self) -> Dict[str, Any]:
        """Main method to send container information."""
        try:
            self.logger.info("Starting main method to send container information")
            return self.send_info(self.name, self.master_url)
        
        except Exception as e:
            self.logger.error(f"Failed to send container information: {str(e)}")
            raise
