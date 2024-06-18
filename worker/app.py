import uuid
import threading
from flask import Flask
from flask_restful import Api

from worker.conf.config import CONFIG
from worker.ImagePuller import ImagePuller
from worker.InfoSender import InfoSender
from worker.ImageRunner import ImageRunner
from worker.cli import get_arguments

# Initialize Flask
app = Flask(__name__)
api = Api(app)

# Enable debug mode for the Flask app
app.debug = True

# Add routes for resources based on configuration
api.add_resource(
    ImagePuller,
    CONFIG.get("routes", {}).get("worker", {}).get("pull_image")
)
api.add_resource(
    ImageRunner,
    CONFIG.get("routes", {}).get("worker", {}).get("run_image")
)

def start_info_sender(args) -> None:
    """Start InfoSender instance in a separate thread."""
    infoSender = InfoSender(str(uuid.uuid4()), args)
    infoSender.main()

def main() -> None:
    """
    If --master-ip is provided in command-line arguments, start InfoSender in a thread.
    Otherwise, run the Flask app on specified host and port.
    """
    args = get_arguments()
    if args.master_ip:
        # Create a thread for starting InfoSender
        info_sender_thread = threading.Thread(target=start_info_sender, args=(args,))
        info_sender_thread.start()  # Start InfoSender thread

        # Wait for InfoSender thread to complete
        info_sender_thread.join()
    else:
        # Run the Flask app in the main thread using specified host and port from configuration
        app.run(host=CONFIG.get('host'), port=CONFIG.get('port'))

if __name__ == "__main__":
    main()
