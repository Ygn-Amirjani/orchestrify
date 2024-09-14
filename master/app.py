import threading
import logging
import signal
import sys
from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from typing import Any

from master.conf.config import CONFIG
from master.WorkerRegistrer import WorkerRegistrer
from master.WorkerUpdater import WorkerUpdater
from master.WorkerDelete import WorkerDelete
from master.WorkersList import WorkersList
from master.WorkerInfo import WorkerInfo
from master.ImageDeploymentHandler import ImageDeploymentHandler
from master.DeployImage import DeployImage
from master.WorkerSelector import WorkerSelector
from master.ContainersList import ContainersList
from master.ContainerInfo import ContainerInfo
from master.ContainerDeleter import ContainerDeleter
from master.NotificationHandler import NotificationHandler
from master.ContainerFetcher import ContainerFetcher
from master.ContainerStatusReceiver import ContainerStatusReceiver
from master.ContainerReallocator import ContainerReallocator
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

# Enable CORS for all routes
CORS(app)

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
    resource_class_kwargs={'repository': db, 'master_ip': CONFIG.get('host')}
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
    ContainerDeleter,
    CONFIG.get('routes', {}).get('master', {}).get('container_delete'),
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
api.add_resource(
    ContainerReallocator,
    CONFIG.get('routes', {}).get('master', {}).get('container_reallocator'),
    resource_class_kwargs={'repository': db}
)
api.add_resource(
    DeployImage,
    CONFIG.get('routes', {}).get('master', {}).get('deploy_image'),
    resource_class_kwargs={'repository': db}
)

def fetch_and_print_workers() -> None:
    """Fetch and print the list of workers."""
    try:
        workers_list = WorkersList(db)
        workers, status = workers_list.get()
        if status == 200:
            print("List of workers:\n")
            for worker in workers:
                print(worker)
        else:
            print(f"Failed to retrieve workers. Status code: {status}")
    except Exception as e:
       logger.error(f"Failed to retrieve worker list: {e}")

def fetch_worker(worker_id: str) -> None:
    """Fetch and print the information of worker."""
    try:
        workers_info = WorkerInfo(db)
        worker_info, status = workers_info.get(worker_id)

        if status == 200:
            print("Worker information:\n")
            print(worker_info)
        else:
            print(f"Failed to retrieve worker. Status code: {status}, Error: {worker_info['error']}")
    except Exception as e:
       logger.error(f"Failed to retrieve worker information: {e}")

def delete_worker(worker_id: str) -> None:
    worker_delete = WorkerDelete(db, CONFIG.get('host'))
    worker_info, status = worker_delete.delete(worker_id)

    if status == 200:
        print('worker is deleted')
        print(worker_info)
    else:
        print('failed to delete worker')

def fetch_and_print_containers() -> None:
    """Fetch and print the list of workers."""
    try:
        containers_list = ContainersList(db)
        containers, status = containers_list.get()
        if status == 200:
            print("List of containers:\n")
            for container in containers:
                print(container)
        else:
            print(f"Failed to retrieve containers. Status code: {status}")
    except Exception as e:
       logger.error(f"Failed to retrieve containers list: {e}")

def fetch_container(container_id: str) -> None:
    """Fetch and print the information of container."""
    try:
        containers_info = ContainerInfo(db)
        container_info, status = containers_info.get(container_id)

        if status == 200:
            print("container information:\n")
            print(container_info)
        else:
            print(f"Failed to retrieve container. Status code: {status}, Error: {container_info['error']}")
    except Exception as e:
        logger.error(f"Failed to retrieve container information: {e}")

def delete_container(container_id: str) -> None:
    container_delete = ContainerDeleter(db)
    container_info, status = container_delete.delete(container_id)

    if status == 200:
        print('container is deleted')
        print(container_info)
    else:
        print('failed to delete container')

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
    print("Shutting down gracefully...")
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

        if args.nodes:
            # Handle the --nodes argument by fetching and printing worker list
            fetch_and_print_workers()
        elif args.node:
            # Handle the --node ID argument by fetching and printing worker information
            fetch_worker(args.node)
        elif args.node_del:
            delete_worker(args.node_del) 
        elif args.procs:
            # Handle the --procs argument by fetching and printing container list
            fetch_and_print_containers()
        elif args.proc:
            # Handle the --proc ID argument by fetching and printing container information
            fetch_container(args.proc)
        elif args.proc_del:
            delete_container(args.proc_del)
        elif args.image_name:
            # Create a thread for starting imageDeploymentHandler
            image_sender_thread = threading.Thread(target=start_image_deployment_handler, args=(args,))
            image_sender_thread.start() # Start imageDeploymentHandler thread

            # Wait for imageDeploymentHandler thread to complete
            image_sender_thread.join()
        else:

            # Start ContainerStatusReceiver thread
            stop_event = threading.Event()
            start_container_status_receiver = start_container_status_receiver(stop_event)

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
