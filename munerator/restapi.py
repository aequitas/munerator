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
from flask import Flask, url_for
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer
from zmq.eventloop import ioloop
from zmq.eventloop.zmqstream import ZMQStream

from .misc import crossdomain

log = logging.getLogger(__name__)


# global stores
players = {}
games = {}

# setup some zmq/tornado binding
ioloop.install()

# setup flask app
app = Flask(__name__, static_url_path='')


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

        # get player and/or game id from data
        player_id = data.get('client_info', {}).get('guid')
        game_id = data.get('game_info', {}).get('id')

        # handle player events
        if player_id:
            if player_id not in players:
                players[player_id] = dict()
            player = players.get(player_id)

            if kind == 'clientbegin':
                player['team'] = data['client_info']['team']
                player['name'] = data['client_info']['name']
                player['id'] = player_id
                player['online'] = True
                player['games'] = []
                player['score'] = 0
            elif kind == 'clientdisconnect':
                player['online'] = False

            if game_id and game_id in games:
                if player_id not in games[game_id]['players']:
                    games[game_id]['players'].append(player_id)

        # handle map events
        elif kind == 'initgame':
            games[game_id] = dict()
            games[game_id]['id'] = game_id
            games[game_id]['mapname'] = data['mapname']
            games[game_id]['current'] = True
            games[game_id]['players'] = list()
            games[game_id]['start'] = data['game_info']['start_ts']
        elif kind == 'shutdowngame':
            if game_id in games:
                games[game_id]['current'] = False
                games[game_id]['stop'] = data['game_info']['stop_ts']


@app.route('/')
def root():
    return app.send_static_file('index.html')


@app.route('/api/1/')
def api_index():
    return json.dumps({
        'players': url_for('get_players', _external=True),
        'maps': url_for('get_maps', _external=True)
    })


@app.route("/api/1/players")
@crossdomain('*')
def get_players():
    return json.dumps({'players': players.values()})


@app.route('/api/1/players/<player_id>', methods=['GET'])
@crossdomain('*')
def get_player(player_id):
    return json.dumps({'player': players[player_id]})


@app.route("/api/1/games")
@crossdomain('*')
def get_games():
    return json.dumps({'games': games.values()})


@app.route('/api/1/games/<game_id>', methods=['GET'])
@crossdomain('*')
def get_game(game_id):
    return json.dumps({'game': games[game_id]})


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
