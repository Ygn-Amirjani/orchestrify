from flask import request, Response, jsonify
from flask_restful import Resource
from master.loadbalancer.ContainerInfoSender import ContainerInfoSender
import requests
import random

class Proxy(Resource):
    def __init__(self, master_url: str) -> None:
        self.master_url = master_url

    def post(self):
        try:
            data = request.json
            if not data or 'name' not in data:
                return Response(
                    'image name not provided', 
                    status=400, 
                    content_type='text/plain'
                )

            container_name = data['name']
            method = data.get('method', 'GET').upper()
            headers = data.get('headers', {})
            payload = data.get('payload', {})

            # Send the request and measure response time
            response = None
            response_time = None

            infoSender = ContainerInfoSender(container_name,self.master_url)
            ip = random.choice(infoSender.main().get("ip"))
            port = infoSender.main().get("port")
            url = f"http://{ip}:{port}/"

            if method == 'GET':
                response = requests.get(url, headers=headers, params=payload)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=payload)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=payload)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, json=payload)
            else:
                return Response('Unsupported HTTP method', status=400, content_type='text/plain')

            # Convert to milliseconds
            response_time = response.elapsed.total_seconds() * 1000

            # Check if response time is less than or equal to 100 milliseconds
            if response_time <= 100:
                excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
                headers = [(name, value) for name, value in response.raw.headers.items()
                           if name.lower() not in excluded_headers]

                return Response(
                    response.content, 
                    status=response.status_code, 
                    headers=headers
                )
            else:
                notify_response = requests.post(f'{self.master_url}/notification', json=url)
                notify_response.raise_for_status()
                return jsonify({'message': 'Response time exceeds 100 milliseconds. Request not sent.'})

        except Exception as e:
            return Response(str(e), status=500, content_type='text/plain')
