import uuid
import threading
from flask import Flask
from flask_restful import Api

from worker.conf.config import CONFIG
from worker.ImagePuller import ImagePuller
from worker.InfoSender import InfoSender
from worker.ImageRunner import ImageRunner
from worker.cli import get_arguments

app = Flask(__name__)
api = Api(app)

app.debug = True

# Add the resource to the API
api.add_resource(ImagePuller, CONFIG.get("routes", {}).get("worker", {}).get("pull"))
api.add_resource(ImageRunner, CONFIG.get("routes", {}).get("worker", {}).get("run"))

def start_info_sender(args):
    worker_id = str(uuid.uuid4())
    path = CONFIG.get('routes', {}).get('master', {}).get('register')
    infoSender = InfoSender(worker_id, args, path)
    infoSender.main()

def main():
    args = get_arguments()
    if args.master_ip:
            info_sender_thread = threading.Thread(target=start_info_sender, args=(args,))
            info_sender_thread.start()
            info_sender_thread.join()
    else:
        # Run the Flask app in the main thread
        app.run(host=CONFIG.get('host'), port=CONFIG.get('port'))

if __name__ == "__main__":
    main()
