import threading
from flask import Flask
from flask_restful import Api

from master.conf.config import CONFIG
from master.WorkerRegistrar import WorkerRegistrar
from master.WorkerUpdater import WorkerUpdater
from master.WorkersList import WorkersList
from master.WorkerInfo import WorkerInfo
from master.ImageSender import ImageSender
from master.cli import get_arguments

from master.database.RedisDB import Redis

app = Flask(__name__)
api = Api(app)

app.debug = True

db = Redis()

api.add_resource(
    WorkerRegistrar,
    CONFIG.get('routes', {}).get('master', {}).get('register'),
    resource_class_kwargs={'repository': db}
)
api.add_resource(
    WorkerUpdater,
    CONFIG.get('routes', {}).get('master', {}).get('update'),
    resource_class_kwargs={'repository': db}
)
api.add_resource(
    WorkersList,
    CONFIG.get('routes', {}).get('master', {}).get('list'),
    resource_class_kwargs={'repository': db}
)
api.add_resource(
    WorkerInfo,
    CONFIG.get('routes', {}).get('master', {}).get('info'),
    resource_class_kwargs={'repository': db}
)

def start_image_sender(args):
    port = CONFIG.get('routes', {}).get('worker', {}).get('port')
    path = CONFIG.get('routes', {}).get('worker', {}).get('pull')
    imageSender = ImageSender(db, args, port, path)
    imageSender.main()

def main():
    args = get_arguments()
    if args.image_name:
        image_sender_thread = threading.Thread(target=start_image_sender, args=(args,))
        image_sender_thread.start()
    else:
        # Run the Flask app in the main thread
        app.run(host=CONFIG.get('host'), port=CONFIG.get('port'))

if __name__ == "__main__":
    main()
