"""Run HTTP REST API with live game data

Usage:
  munerator [options] restapi

Options:
  -v --verbose            Verbose logging
  --context-socket url    ZMQ socket for conext event [default: tcp://127.0.0.1:9002]
  --http-listen ip:port   Host and port to have the HTTP server listen on [default: 0.0.0.0:8081]

"""
import json
import logging
from functools import partial

import zmq
from docopt import docopt
from flask import Flask
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer
from zmq.eventloop import ioloop
from zmq.eventloop.zmqstream import ZMQStream

from .misc import crossdomain

log = logging.getLogger(__name__)


# global stores
players = {}
maps = {}

# setup some zmq/tornado binding
ioloop.install()

# setup flask app
app = Flask(__name__)


def handle_events(msgs):
    for msg in msgs:
        try:
            handle_event(msg)
        except:
            log.exception('error in handle_event')


def handle_event(msg):
        kind, raw_data = msg.split(' ', 1)
        log.debug('in data: %s' % raw_data)
        if not raw_data:
            return
        data = json.loads(raw_data)

        # handle player events
        client_id = data.get('client_id', '')
        if client_id.isdigit():
            player = players.get(client_id, dict())
            if kind == 'clientbegin':
                player['team'] = data['client_info']['team']
                player['name'] = data['client_info']['name']
                player['id'] = data['client_info']['']
                players[client_id] = player
            elif kind == 'clientdisconnect':
                del players[client_id]

        # handle map events
        elif kind == 'initgame':
            maps['current'] = dict()
            maps['current']['id'] = data['id']
            maps['current']['name'] = data['mapname']
            maps['current']['current'] = True
        elif kind == 'shutdowngame':
            if maps.get('current'):
                maps['previous'] = maps['current']
                maps['previous']['current'] = False


@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route("/players")
@crossdomain('*')
def get_players():
    return json.dumps({'players': players.values()})


@app.route("/maps")
@crossdomain('*')
def get_maps():
    return json.dumps({'maps': maps.values()})


def main(argv):
    args = docopt(__doc__, argv=argv)

    # init zmq listening connection
    context = zmq.Context()
    in_socket = context.socket(zmq.SUB)
    in_socket.connect(args['--context-socket'])

    # subscribe to relevant events
    filters = ['initgame', 'shutdowngame', 'clientdisconnect', 'clientbegin', 'clientuserinfochanged']
    add_filter = partial(in_socket.setsockopt, zmq.SUBSCRIBE)
    map(add_filter, filters)

    # configure zmq in socket callback
    in_events = ZMQStream(in_socket)
    in_events.on_recv(handle_events)

    # configure flask app callback
    host, port = args['--http-listen'].split(':')
    http_server = HTTPServer(WSGIContainer(app))
    http_server.listen(port, address=host)

    # run event loop
    IOLoop.instance().start()
