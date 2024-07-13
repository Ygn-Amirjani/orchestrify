from typing import Dict, Any
import requests

class ContainerInfoSender:
    def __init__(self, container_name: str, master_url: str) -> None:
        self.name = container_name
        self.master_url = master_url

    def post(self, url: str, data: str) -> requests.Response:
        """Perform a POST request."""
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response

        except requests.exceptions.RequestException as e:
            print(f"Error during POST request to {url}: {e}")
            raise

    def send_info(self, container_name: str) -> Dict[str, Any]:
        """Send container information to the master server."""
        try:
            result = self.post(f"{self.master_url}/container_fetcher", container_name)
            if result.status_code == 200:
                print("Container IP sent successfully")

                data = {
                    "ip": result.json().get("ips"),
                    "port": result.json().get("port")
                }
                return data
            else:
                print(result.text)
                raise Exception(f"Sending container IP failed with status code {result.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"Request error: {str(e)}")
            raise

        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            raise

    def main(self) -> Dict[str, Any]:
        """Main method to send container information."""
        try:
            return self.send_info(self.name)
        
        except Exception as e:
            print(f"Failed to send container information: {str(e)}")
            raise
