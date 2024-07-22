import threading
import logging
import signal
import sys
from flask import Flask
from flask_restful import Api
from typing import Any

from master.conf.config import CONFIG
from master.WorkerRegistrer import WorkerRegistrer
from master.WorkerUpdater import WorkerUpdater
from master.WorkerDelete import WorkerDelete
from master.WorkersList import WorkersList
from master.WorkerInfo import WorkerInfo
from master.ImageDeploymentHandler import ImageDeploymentHandler
from master.WorkerSelector import WorkerSelector
from master.ContainersList import ContainersList
from master.ContainerInfo import ContainerInfo
from master.NotificationHandler import NotificationHandler
from master.ContainerFetcher import ContainerFetcher
from master.ContainerStatusReceiver import ContainerStatusReceiver
from master.cli import get_arguments
from master.conf.logging_config import setup_logging
from master.database.RedisDB import Redis

# Set up logging for the main module
log_file = "logs/master_app.log"
setup_logging(log_file)
logger = logging.getLogger(__name__)

# Initialize Flask
app = Flask(__name__)
api = Api(app)

# Enable debug mode for the Flask app
app.debug = True

#  Instantiate the Redis class and creating a connection to the Redis database
db = Redis()

# Add routes for resources based on configuration
api.add_resource(
    WorkerRegistrer,
    CONFIG.get('routes', {}).get('master', {}).get('worker_register'), 
    resource_class_kwargs={'repository': db}
)
api.add_resource(
    WorkerUpdater,
    CONFIG.get('routes', {}).get('master', {}).get('worker_updater'),
    resource_class_kwargs={'repository': db}
)
api.add_resource(
    WorkerDelete,
    CONFIG.get('routes', {}).get('master', {}).get('worker_delete'),
    resource_class_kwargs={'repository': db}
)
api.add_resource(
    WorkersList,
    CONFIG.get('routes', {}).get('master', {}).get('workers_list'),
    resource_class_kwargs={'repository': db}
)
api.add_resource(
    WorkerInfo,
    CONFIG.get('routes', {}).get('master', {}).get('worker_info'),
    resource_class_kwargs={'repository': db}
)
api.add_resource(
    ContainersList,
    CONFIG.get('routes', {}).get('master', {}).get('containers_list'),
    resource_class_kwargs={'repository': db}
)
api.add_resource(
    ContainerInfo,
    CONFIG.get('routes', {}).get('master', {}).get('container_info'),
    resource_class_kwargs={'repository': db}
)
api.add_resource(
    NotificationHandler,
    CONFIG.get('routes', {}).get('master', {}).get('notification'),
    resource_class_kwargs={'repository': db}
)
api.add_resource(
    ContainerFetcher,
    CONFIG.get('routes', {}).get('master', {}).get('Container_fetcher'),
    resource_class_kwargs={'repository': db}
)

def start_image_deployment_handler(args) -> None:
    """Start ImageDeploymentHandler instance in a separate thread."""
    try:
        workers_list = WorkersList(db)
        workers, status = workers_list.get()
        workerSelector = WorkerSelector(db,workers)
        imageHandler = ImageDeploymentHandler(db, args, workerSelector.main())
        imageHandler.main()

    except Exception as e:
        logger.error(f"Exception occurred during image deployment: {str(e)}")

def start_container_status_receiver(stop_event: threading.Event) -> None:
    """Start ContainerStatusReceiver in a separate thread."""
    try:
        status_receiver = ContainerStatusReceiver(db, stop_event)
        status_receiver.main()
    except Exception as e:
        logger.error(f"Exception occurred in ContainerStatusReceiver: {str(e)}")

def signal_handler(signal: int, frame: Any) -> None:
    """Handle signal interruption."""
    logger.info("Shutting down gracefully...")
    if 'start_container_status_receiver' in globals():
        start_container_status_receiver.stop()  # Stop the start_container_status_receiver thread
    sys.exit(0)


def main() -> None:
    """
    If --image-name is provided in command-line arguments,start function in a thread.
    Otherwise, run the Flask app on specified host and port.
    """
    global start_container_status_receiver
    try:
        args = get_arguments()

        # Start ContainerStatusReceiver thread
        stop_event = threading.Event()
        start_container_status_receiver = start_container_status_receiver(stop_event)

        if args.image_name:
            # Create a thread for starting imageDeploymentHandler
            image_sender_thread = threading.Thread(target=start_image_deployment_handler, args=(args,))
            image_sender_thread.start() # Start imageDeploymentHandler thread

            # Wait for imageDeploymentHandler thread to complete
            image_sender_thread.join()
        else:
            # Run the Flask app in the main thread using specified host and port from configuration
            app.run(host=CONFIG.get('host'), port=CONFIG.get('port'))

    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")

    except Exception as e:
        logger.error(f"Unhandled exception in main thread: {str(e)}")

if __name__ == "__main__":
    # Register signal handler
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    main()
