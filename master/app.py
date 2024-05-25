import threading
from flask import Flask
from flask_restful import Api

from master.conf.config import CONFIG
from master.WorkerRegistrer import WorkerRegistrer
from master.WorkerUpdater import WorkerUpdater
from master.WorkersList import WorkersList
from master.WorkerInfo import WorkerInfo
from master.ImageDeploymentHandler import ImageDeploymentHandler
from master.cli import get_arguments

from master.database.RedisDB import Redis

app = Flask(__name__)
api = Api(app)

app.debug = True

db = Redis()

master_path = CONFIG.get('routes', {}).get('master', {})
kwargs = {'repository': db}

api.add_resource(WorkerRegistrer, master_path.get('register'), resource_class_kwargs=kwargs)
api.add_resource(WorkerUpdater, master_path.get('update'), resource_class_kwargs=kwargs)
api.add_resource(WorkersList, master_path.get('list'), resource_class_kwargs=kwargs)
api.add_resource(WorkerInfo, master_path.get('info'), resource_class_kwargs=kwargs)

def start_image_sender(args):
    port = CONFIG.get('routes', {}).get('worker', {}).get('port')
    pull_path = CONFIG.get('routes', {}).get('worker', {}).get('pull')
    run_path = CONFIG.get('routes', {}).get('worker', {}).get('run')
    imageHandler = ImageDeploymentHandler(db, args, port, pull_path, run_path)
    imageHandler.main()

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
