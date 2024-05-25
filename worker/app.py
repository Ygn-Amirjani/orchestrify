from flask import Flask
from flask_restful import Api

from worker.conf.config import CONFIG
from worker.ImagePuller import ImagePuller

app = Flask(__name__)
api = Api(app)

app.debug = True

# Add the resource to the API
api.add_resource(
    ImagePuller,
    CONFIG.get('routes', {}).get('worker', {}).get('pull')
)

if __name__ == "__main__":
    app.run(host=CONFIG.get('host'), port=CONFIG.get('port'))
