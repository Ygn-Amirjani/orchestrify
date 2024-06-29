from flask import Flask
from flask_restful import Api

from master.conf.config import CONFIG
from master.loadbalancer.Proxy import Proxy

app = Flask(__name__)
api = Api(app)

app.debug = True

api.add_resource(Proxy, CONFIG.get('loadbalancer', {}).get('proxy'))

if __name__ == '__main__':
    app.run(
        host=CONFIG.get('loadbalancer', {}).get('host'),
        port=CONFIG.get('loadbalancer', {}).get('port')
    )
