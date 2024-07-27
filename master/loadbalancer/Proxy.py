from collections import deque
from flask import request, Response
from flask_restful import Resource
from typing import Dict, Any, Union, Deque
from master.loadbalancer.ContainerInfoSender import ContainerInfoSender
from master.conf.logging_config import setup_logging

import requests
import logging


class Proxy(Resource):
    def __init__(self, master_url: str) -> None:
        self.master_url = master_url
        log_file = "logs/loadbalancer.log"
        setup_logging(log_file)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.servers_queue: Deque[str] = deque()

    def round_robin_load_balancing(self, available_servers_queue: list[str]) -> str:
        """Select one of the available servers using RoundRobin load balancing algorithm"""

        if len(available_servers_queue) == 0:
            raise ValueError("There aren't any servers available!")

        # Init round
        if len(self.servers_queue) == 0:
            for s in available_servers_queue:
                self.servers_queue.append(s)

        current_server = self.servers_queue.popleft()

        # Greedily update servers list with available servers
        while current_server not in set(available_servers_queue):
            self.servers_queue.remove(current_server)
            current_server = self.servers_queue.popleft()

        # Put server in the end of the list
        self.servers_queue.append(current_server)
        return current_server

    def find_container_url(self, container_info: Dict[str, Any]) -> str:
        """Find the container URL from the container information."""
        ip = self.round_robin_load_balancing(container_info.get("ip"))
        port = container_info.get("port")
        url = f"http://{ip}:{port}"
        self.logger.debug(f"Container URL found: {url}")

        return url

    def send_request(self, data: Dict[str, Any], url: str) -> requests.Response:
        """Send a request to the container."""
        method = data.get("method", "GET").upper()
        headers = data.get("headers", {})
        payload = data.get("payload", {})

        self.logger.debug(
            f"Sending {method} request to {url} with headers {headers} and payload {payload}"
        )
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=payload)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=payload)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json=payload)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, json=payload)
            else:
                self.logger.error(f"Unsupported HTTP method: {method}")
                return Response(
                    "Unsupported HTTP method", status=400, content_type="text/plain"
                )

            self.logger.debug(f"Received response with status {response.status_code}")
            return response

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error occurred: {e}")
            raise

    def build_response(self, response: requests.Response) -> Response:
        """Build a Flask response from the requests response."""
        excluded_headers = [
            "content-encoding",
            "content-length",
            "transfer-encoding",
            "connection",
        ]
        headers = [
            (name, value)
            for name, value in response.raw.headers.items()
            if name.lower() not in excluded_headers
        ]

        response = Response(
            response.content, status=response.status_code, headers=headers
        )
        self.logger.debug(f"Built Flask response with status {response.status_code}")
        return response

    def post(self) -> Union[Response, Dict[str, Any]]:
        """Handle POST requests to the proxy."""
        try:
            data = request.json
            if not data or "name" not in data:
                self.logger.error("Image name not provided in request data")
                return Response(
                    "Image name not provided", status=400, content_type="text/plain"
                )

            self.logger.info(f"Received request to proxy for image: {data['name']}")
            infoSender = ContainerInfoSender(data["name"], self.master_url)
            container_info = infoSender.main()

            url = self.find_container_url(container_info)
            response = self.send_request(data, url)

            # Convert to milliseconds
            response_time = response.elapsed.total_seconds() * 1000
            self.logger.info(f"Received request to proxy for image: {data['name']}")

            # Check if response time is less than or equal to 100 milliseconds
            if response_time >= 100:
                self.logger.info("Response time within acceptable range")
                return self.build_response(response)
            else:
                self.logger.warning("Response time exceeded 100 ms, notifying master")
                notify_response = requests.post(
                    f"{self.master_url}/notification", json=container_info
                )
                if notify_response.status_code == 200:
                    self.logger.info("Master notified successfully")
                    return self.build_response(
                        response
                    )  # Return the answer with the new container should be fixed
                else:
                    self.logger.error(
                        f"Failed to notify master: {notify_response.status_code}"
                    )
                    return notify_response.json()

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error occurred: {e}")
            return Response(
                "Request error occurred", status=500, content_type="text/plain"
            )

        except Exception as e:
            self.logger.error(f"Unexpected error occurred: {e}")
            return Response(
                "Unexpected error occurred", status=500, content_type="text/plain"
            )
