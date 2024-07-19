import uuid
import threading
import logging
import signal
import sys
from flask import Flask
from flask_restful import Api
from typing import Any

from worker.conf.config import CONFIG
from worker.ImagePuller import ImagePuller
from worker.InfoSender import InfoSender
from worker.ImageRunner import ImageRunner
from worker.cli import get_arguments
from worker.conf.logging_config import setup_logging

# Set up logging for the main module
log_file = "logs/worker_app.log"
setup_logging(log_file)
logger = logging.getLogger(__name__)

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

def start_info_sender(args, stop_event: threading.Event) -> InfoSender:
    """Start InfoSender instance in a separate thread."""
    try:
        info_sender = InfoSender(str(uuid.uuid4()), args, stop_event)
        info_sender.main()
        return info_sender

    except Exception as e:
        logger.error(f"An error occurred in InfoSender: {e}")

def signal_handler(signal: int, frame: Any) -> None:
    """Handle signal interruption."""
    logger.info("Shutting down gracefully...")
    if 'info_sender_instance' in globals():
        info_sender_instance.stop()  # Stop the InfoSender thread
    sys.exit(0)

def main() -> None:
    """
    If --master-ip is provided in command-line arguments, start InfoSender in a thread.
    Otherwise, run the Flask app on specified host and port.
    """
    global info_sender_instance
    try:
        args = get_arguments()
        
        if args.master_ip:
            # Start InfoSender in a separate thread
            stop_event = threading.Event()
            info_sender_instance = start_info_sender(args, stop_event)

        else:
            # Run the Flask app in the main thread
            app.run(host=CONFIG.get('host'), port=CONFIG.get('port'))

    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":  
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    main()
