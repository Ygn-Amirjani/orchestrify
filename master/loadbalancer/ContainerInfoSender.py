import requests

class ContainerInfoSender:
    def __init__(self, container_name: str, master_url: str) -> None:
        self.name = container_name
        self.master_url = master_url

    def post(self, url: str, data: str) -> requests.Response:
        """Perform a POST request."""
        return requests.post(url, json=data)

    def send_info(self, container_name):
        result = self.post(f"{self.master_url}/container_fetcher", container_name)
        if result.status_code == 200:
            print("Container ip Sender successfully")

            data = {
                "ip": result.json().get("ips"),
                "port": result.json().get("port")
            }
            return data
        else:
            print(result.text)
            raise Exception(f"Send Container ip failed {result.status_code}")

    def main(self):
        return self.send_info(self.name)
