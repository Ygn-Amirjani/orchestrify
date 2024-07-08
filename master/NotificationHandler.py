from flask_restful import Resource
from flask import request
from master.database.Repository import Repository
from master.ContainersList import ContainersList
from master.ContainerInfo import ContainerInfo

class NotificationHandler(Resource):
    def __init__(self, repository: Repository) -> None:
        self.repository = repository
        self.containers_list = ContainersList(repository)
        self.container_info = ContainerInfo(repository)

    def post(self):
        master_url = request.get_json()
        ip = master_url.split("//")[1].split(":")[0]
        port = master_url.split("//")[1].split(":")[1]

        container_keys, status = self.containers_list.get()

        for container_key in container_keys:
            container_info, status = self.container_info.get(container_key)
            if container_info.get('worker_ip') == ip and \
               container_info.get('port') == port:
                print(container_info)
                print('--------------------------')
