from flask import Flask
from flask_restful import Api
import logging

from master.conf.config import CONFIG
from master.loadbalancer.Proxy import Proxy
from master.conf.logging_config import setup_logging

# Set up logging for the main module
log_file = "logs/loadbalancer.log"
setup_logging(log_file)
logger = logging.getLogger(__name__)

# Initialize Flask
app = Flask(__name__)
api = Api(app)

# Enable debug mode for the Flask app
app.debug = True

master_url = f"http://{CONFIG.get('host')}:{CONFIG.get('port')}"

# Add routes for resources based on configuration
api.add_resource(
    Proxy,
    CONFIG.get('loadbalancer', {}).get('proxy'),
    resource_class_kwargs={'master_url': master_url}    
)

# app
if __name__ == '__main__':
    app.run(
        host=CONFIG.get('loadbalancer', {}).get('host'),
        port=CONFIG.get('loadbalancer', {}).get('port')
    )
