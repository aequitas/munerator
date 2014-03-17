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
log = logging.getLogger(__name__)

import json


class GameContext(object):
    def __init__(self):
        self.start_ts = 0
        self.stop_ts = 0

        self.gameinfo = {'clients': {}}

    def eventstream(self, in_socket, out_socket):
        while True:
            data = in_socket.recv_json()
            log.debug(' in: %s' % data)

            kind = data.get('kind')
            ts = data.get('timestamp')
            client_id = data.get('client_id')

            if kind == 'initgame':
                self.start_ts = ts
                self.gameinfo = {
                    'mapname': data.get('mapname'),
                    'clients': {}
                }
            elif kind == 'clientuserinfochanged':
                log.debug('setting client info: %s' % client_id)
                self.gameinfo['clients'][client_id] = {
                    'name': data.get('player_name'),
                    'guid': data.get('guid'),
                    'client_id': client_id
                }

            # add game context to event
            if self.start_ts < ts > self.stop_ts:
                data['game_info'] = self.gameinfo

            if kind == 'clientdisconnect':
                try:
                    del self.gameinfo['clients'][client_id]
                except KeyError:
                    pass
            elif kind == 'shutdowngame':
                self.stop_ts = ts
                self.gameinfo = {'clients': {}}

            log.debug('out: %s' % data)
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
