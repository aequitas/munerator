"""Add game and player context to events

Usage:
  munerator [options] context

Options:
  -v --verbose          Verbose logging
  --events-socket url   ZMQ socket for raw events [default: tcp://127.0.0.1:9001]
  --context-socket url  ZMQ socket for context events [default: tcp://0.0.0.0:9002]
  --rcon-socket url     ZMQ socket for rcon commands [default: tcp://127.0.0.1:9005]

"""
from docopt import docopt
import zmq
import logging
import collections
import json
import time
import dateutil.parser

log = logging.getLogger(__name__)


team_id_map = ['', 'blue', 'red', 'spectator']
deduplicate = collections.deque(maxlen=5)


def get_dict_value_from_key_if_key_value(data, value_key, query_key, query_value):
    item = [v for k, v in data.items() if v.get(query_key) == query_value]
    if item:
        return item[0].get(value_key)


class GameContext(object):

    def __init__(self, in_socket, out_socket, rcon_socket):
        self.gameinfo = {}
        self.clients = {}

        self.in_socket = in_socket
        self.out_socket = out_socket
        self.rcon_socket = rcon_socket

    def eventstream(self):
        # prime commands for current game info
        self.rcon_socket.send_string('status')
        self.rcon_socket.send_string('getstatus')

        while True:
            data = self.in_socket.recv_json()
            log.debug('   in: %s' % data)

            if str(data) in deduplicate:
                log.debug('skip')
                continue
            deduplicate.append(str(data))

            contexted_data = self.handle_event(data)

            self.out_socket.send_string("%s %s" % (contexted_data.get('kind'), json.dumps(contexted_data)))

    def handle_event(self, data):
        kind = data.get('kind')
        client_id = data.get('client_id')

        # for some events we need to translate player_name into client_id
        if not client_id and kind in ['say', 'killer', 'killed']:
            client_id = get_dict_value_from_key_if_key_value(
                self.clients, 'client_id', 'name', data.get('player_name'))
            data['client_id'] = client_id

        if kind in ['initgame', 'getstatus']:
            self.gameinfo = {
                'mapname': data.get('mapname'),
                'gametype': data.get('gametype'),
                'timestamp': data.get('timestamp'),
                'start': dateutil.parser.parse(data.get('timestamp')).strftime('%s'),
                'current': True
            }
            if kind == 'initgame':
                self.gameinfo.update({
                    'num_players': 0,
                    'stop': None
                })
                self.clients = {}
        elif kind in ['clientuserinfochanged', 'clientstatus']:
            log.debug('setting client info: %s' % client_id)
            self.clients[client_id] = {
                'name': data.get('player_name'),
                'id': data.get('guid'),
                'guid': data.get('guid'),
                'client_id': client_id,
                'team_id': data.get('team_id'),
                'skill': data.get('skill'),
                'team': team_id_map[int(data.get('team_id', 0))],
                'score': 0,
                'online': True,
                'bot': False
            }
            if data.get('skill') or data.get('address') == 'bot':
                self.clients[client_id]['bot'] = True
            self.gameinfo['num_players'] = len(self.clients)
        elif kind == 'playerscore':
            log.debug('setting client score: %s' % client_id)
            if client_id in self.clients:
                self.clients[client_id]['score'] = data.get('score')
        elif kind == 'clientdisconnect':
            if client_id in self.clients:
                self.clients[client_id]['online'] = False
        elif kind in ['clientstatus', 'clientconnect']:
            # on clientstatus also request dumpuser
            self.rcon_socket.send_string('dumpuser %s' % client_id)

        data['game_info'] = self.gameinfo
        data['client_info'] = self.clients.get(client_id, {})

        if kind == 'clientdisconnect':
            try:
                del self.clients[client_id]
            except KeyError:
                pass
        elif kind == 'shutdowngame':
            # add stop time
            self.gameinfo['stop'] = int(time.time())
            self.gameinfo['current'] = False

            # reset current context
            self.gameinfo = {}
            self.clients = {}

        log.debug(' out: %s' % data)

        return data


def main(argv):
    args = docopt(__doc__, argv=argv)

    context = zmq.Context()
    in_socket = context.socket(zmq.PULL)
    in_socket.bind(args['--events-socket'])

    out_socket = context.socket(zmq.PUB)
    out_socket.bind(args['--context-socket'])

    # setup rcon socket
    rcon_socket = context.socket(zmq.PUSH)
    rcon_socket.connect(args['--rcon-socket'])

    gc = GameContext(in_socket, out_socket, rcon_socket)

    gc.eventstream()
