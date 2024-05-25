from flask import Flask
from flask_restful import Api
import json

from ImagePuller import ImagePuller
from image_runner import ImageRunner

# Load config file
with open("worker/conf/config.json", mode="r") as config_file:
    CONFIG = json.load(config_file)


app = Flask(__name__)
api = Api(app)

app.debug = True

# Add the resource to the API
api.add_resource(ImagePuller, CONFIG.get("routes", {}).get("worker", {}).get("pull"))
api.add_resource(ImageRunner, CONFIG.get("routes", {}).get("worker", {}).get("run"))

if __name__ == "__main__":
    app.run(host=CONFIG.get("host"), port=CONFIG.get("port"))
