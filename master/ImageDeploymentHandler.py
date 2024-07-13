import requests
import argparse
from master.database.Repository import Repository

class ImageDeploymentHandler:
    def __init__(self, repository: Repository, args: argparse.Namespace, worker: str) -> None:
        self.repository = repository
        self.args = args    # Store command-line arguments
        self.worker_url = worker

    def post(self, url: str, data: dict) -> requests.Response:
        """Perform a POST request."""
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            return response

        except requests.exceptions.RequestException as e:
            print(f"Error during POST request to {url}: {e}")
            raise

    def send_image(self, worker_url: str) -> None:
        """Send the image to the worker for pulling."""
        data = self.args.image_name
        try:
            result = self.post(f"{worker_url}/pull_image", data)

            if result.status_code == 200:
                print("Successfully pulled image")
            else:
                print(result.text)
                raise Exception(f"Failed to pull image: {data}. {result.status_code}")

        except Exception as e:
            print(f"Exception occurred during send_image: {str(e)}")
            if "Connection refused" in str(e):
                print("worker server not found. Please check the worker IP address.")
            raise

    def run_image(self, worker_url: str) -> dict:
        """Run the image on the worker."""
        data = {
            "image_name": self.args.image_name,
            "name": self.args.name,
            "network_mode": self.args.network,
            "port": self.args.port,
            "environment": self.args.environment
        }

        # Remove keys with None values
        data = {k: v for k, v in data.items() if v is not None}

        try:
            # Run container on best worker
            result = self.post(f"{worker_url}/run_image", data)

            if result.status_code == 200:
                print("Successfully ran image")
                print(f"container name is: {result.json().get("container_name")}")

                data.update({
                    "worker_ip": worker_url.split("//")[1].split(":")[0],
                    "id": result.json().get("container_id"), 
                    "name": result.json().get("container_name"),
                    "status": result.json().get("container_status")
                })
                return data
            else:
                print(result.text)
                raise Exception(f"Failed to run image: {data}. {result.status_code}")

        except Exception as e:
            print(f"Exception occurred during run_image: {str(e)}")
            if "INTERNAL SERVER ERROR for url" in str(e):
                print("Is the container now running with the same IP and port?")
            raise

    def save_container_info(self, container_info: dict) -> None:
        """Save the container information to the repository."""
        try:
            if container_info.get('port'):
                host_port = next(iter(container_info['port'].values()))
                print (f'Container Url => http://{container_info["worker_ip"]}:{host_port}')

            key = f"{self.args.image_name}:{container_info['id'][0:13]}:{container_info['name']}"
            self.repository.create(f"container:{key}", container_info)

        except Exception as e:
            print(f"Exception occurred during save_container_info: {str(e)}")
            raise

    def main(self) -> None:
        """Main method to manage the deployment process."""
        try:
            self.send_image(self.worker_url)
            container_info = self.run_image(self.worker_url)
            self.save_container_info(container_info)

        except Exception as e:
            print(f"Exception occurred during deployment: {str(e)}")
            raise
