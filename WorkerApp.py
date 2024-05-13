from flask import Flask
from flask_restful import Api

from worker.PullImage import PullImage

app = Flask(__name__)
api = Api(app)

# Add the resource to the API
api.add_resource(
    PullImage,
    '/pull_image'
)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=18081)
