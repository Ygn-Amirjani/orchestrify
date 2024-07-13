from flask import request, Response
from flask_restful import Resource
from master.loadbalancer.ContainerInfoSender import ContainerInfoSender
from typing import Dict, Any, Union

import requests
import random

class Proxy(Resource):
    def __init__(self, master_url: str) -> None:
        self.master_url = master_url

    def find_container_url(self, container_info: Dict[str, Any]) -> str:
        """Find the container URL from the container information."""
        ip = random.choice(container_info.get("ip"))
        port = container_info.get("port")

        return f"http://{ip}:{port}"

    def send_request(self, data: Dict[str, Any], url: str) -> requests.Response:
        """Send a request to the container."""
        method = data.get('method', 'GET').upper()
        headers = data.get('headers', {})
        payload = data.get('payload', {})

        if method == 'GET':
            return requests.get(url, headers=headers, params=payload)
        elif method == 'POST':
            return requests.post(url, headers=headers, json=payload)
        elif method == 'PUT':
            return requests.put(url, headers=headers, json=payload)
        elif method == 'DELETE':
            return requests.delete(url, headers=headers, json=payload)
        else:
            return Response('Unsupported HTTP method', status=400, content_type='text/plain')

    def build_response(self, response: requests.Response) -> Response:
        """Build a Flask response from the requests response."""
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for name, value in response.raw.headers.items()
                   if name.lower() not in excluded_headers]

        return Response(
            response.content, 
            status=response.status_code, 
            headers=headers
        )

    def post(self) -> Union[Response, Dict[str, Any]]:
        """Handle POST requests to the proxy."""
        try:
            data = request.json
            if not data or 'name' not in data:
                return Response(
                    'Image name not provided', 
                    status=400, 
                    content_type='text/plain'
                )

            infoSender = ContainerInfoSender(data['name'], self.master_url)
            container_info = infoSender.main()

            url = self.find_container_url(container_info)
            response = self.send_request(data, url)

            # Convert to milliseconds
            response_time = response.elapsed.total_seconds() * 1000

            # Check if response time is less than or equal to 100 milliseconds
            if response_time <= 100:
                return self.build_response(response)
            else:
                notify_response = requests.post(f'{self.master_url}/notification', json=container_info)
                if notify_response.status_code == 200:
                    return self.build_response(response) # Return the answer with the new container should be fixed
                else:
                    return notify_response.json()

        except Exception as e:
            return Response(str(e), status=500, content_type='text/plain')
