from typing import Dict, Any
import requests

class ContainerInfoSender:
    def __init__(self, container_name: str, master_url: str) -> None:
        self.name = container_name
        self.master_url = master_url

    def post(self, url: str, data: str) -> requests.Response:
        """Perform a POST request."""
        return requests.post(url, json=data)

    def send_info(self, container_name: str) -> Dict[str, Any]:
        """Send container information to the master server."""
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

    def main(self) -> Dict[str, Any]:
        """Main method to send container information."""
        return self.send_info(self.name)
