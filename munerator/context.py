"""Add game and player context to events

Usage:
  munerator [options] context

Options:
  -v --verbose          Verbose logging
  --events-socket url   ZMQ socket for raw events [default: tcp://127.0.0.1:9001]
  --context-socket url  ZMQ socket for context events [default: tcp://0.0.0.0:9002]

"""
from docopt import docopt
import zmq
import logging
import collections
log = logging.getLogger(__name__)

import json

team_id_map = ['', 'blue', 'red', 'spectator']
deduplicate = collections.deque(maxlen=5)


def get_dict_value_from_key_if_key_value(data, value_key, query_key, query_value):
    item = [v for k, v in data.items() if v.get(query_key) == query_value]
    if item:
        return item[0].get(value_key)


class GameContext(object):
    def __init__(self):
        self.start_ts = 0
        self.stop_ts = 0

        self.gameinfo = {}
        self.clients = {}

    def eventstream(self, in_socket, out_socket):
        while True:
            data = in_socket.recv_json()
            log.debug('   in: %s' % data)

            if str(data) in deduplicate:
                log.debug('skip')
                continue
            deduplicate.append(str(data))

            kind = data.get('kind')
            ts = data.get('timestamp')
            client_id = data.get('client_id')

            # for say events we need to translate player name into client_id
            if kind in'say':
                client_id = get_dict_value_from_key_if_key_value(
                    self.clients, 'id', 'name', data.get('player_name'))

            # skip if outside of context
            if ts < self.start_ts:
                log.debug('out of context')
                continue

            if kind == 'initgame':
                self.start_ts = ts
                self.gameinfo = {
                    'mapname': data.get('mapname'),
                    'num_players': 0,
                    'id': int(float(ts)),
                    'start': ts,
                    'stop': None,
                    'current': True
                }
                self.clients = {}
            elif kind == 'clientuserinfochanged':
                log.debug('setting client info: %s' % client_id)
                self.clients[client_id] = {
                    'name': data.get('player_name'),
                    'id': data.get('guid'),
                    'guid': data.get('guid'),
                    'client_id': client_id,
                    'team_id': data.get('team_id'),
                    'team': team_id_map[int(data.get('team_id'))],
                    'score': 0,
                    'online': True
                }
                self.gameinfo['num_players'] = len(self.clients)
            elif kind == 'playerscore':
                log.debug('setting client score: %s' % client_id)
                if client_id in self.clients:
                    self.clients[client_id]['score'] = data.get('score')
            elif kind == 'clientdisconnect':
                if client_id in self.clients:
                    self.clients[client_id]['online'] = False

            data['game_info'] = self.gameinfo
            data['client_info'] = self.clients.get(client_id, {})
            data['clients'] = self.clients

            if kind == 'clientdisconnect':
                try:
                    del self.clients[client_id]
                except KeyError:
                    pass
            elif kind == 'shutdowngame':
                # add stop time
                self.gameinfo['stop'] = ts
                self.gameinfo['current'] = False

                # reset current context
                self.gameinfo = {}
                self.clients = {}

            log.debug(' out: %s' % data)
            out_socket.send_string("%s %s" % (data.get('kind'), json.dumps(data)))


def main(argv):
    args = docopt(__doc__, argv=argv)

    context = zmq.Context()
    in_socket = context.socket(zmq.PULL)
    in_socket.bind(args['--events-socket'])

    out_socket = context.socket(zmq.PUB)
    out_socket.bind(args['--context-socket'])

    gc = GameContext()

    gc.eventstream(in_socket, out_socket)
