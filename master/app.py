import threading
from flask import Flask
from flask_restful import Api

from master.conf.config import CONFIG
from master.WorkerRegistrer import WorkerRegistrer
from master.WorkerUpdater import WorkerUpdater
from master.WorkersList import WorkersList
from master.WorkerInfo import WorkerInfo
from master.ImageDeploymentHandler import ImageDeploymentHandler
from master.WorkerSelector import WorkerSelector
from master.ContainersList import ContainersList
from master.ContainerInfo import ContainerInfo
from master.NotificationHandler import NotificationHandler
from master.ContainerFetcher import ContainerFetcher
from master.cli import get_arguments

from master.database.RedisDB import Redis

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
    workers_list = WorkersList(db)
    workers, status = workers_list.get()
    workerSelector = WorkerSelector(db,workers)
    imageHandler = ImageDeploymentHandler(db, args, workerSelector.main())
    imageHandler.main()

def main() -> None:
    """
    If --image-name is provided in command-line arguments,start function in a thread.
    Otherwise, run the Flask app on specified host and port.
    """
    args = get_arguments()
    if args.image_name:
        # Create a thread for starting InfoSender
        image_sender_thread = threading.Thread(target=start_image_deployment_handler, args=(args,))
        image_sender_thread.start() # Start InfoSender thread

        # Wait for InfoSender thread to complete
        image_sender_thread.join()
    else:
        # Run the Flask app in the main thread using specified host and port from configuration
        app.run(host=CONFIG.get('host'), port=CONFIG.get('port'))

if __name__ == "__main__":
    main()
