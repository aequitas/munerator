"""Display game events on ledbar

Usage:
  munerator [options] ledbar

Options:
  -v --verbose          Verbose logging
  --context-socket url  ZMQ socket for context events [default: tcp://quake.brensen.com:9002]

"""
from docopt import docopt
import zmq
import logging
log = logging.getLogger(__name__)

from functools import partial
import json


def update_ledbar(in_socket):
    state = {}

    while True:
        msg = in_socket.recv_string()

        if msg:
            log.debug('got : %s' % msg)

            data = json.loads(msg.split(' ', 1)[-1])
            kind = data.get('kind')
            client_id = data.get('client_id')

            if not client_id in state:
                state[client_id] = {}
            c = state[client_id]

        if client_id:
            if kind == 'hit':
                c['health'] = data.get('health')
            elif kind == 'playerscore':
                c['score'] = data.get('score')
            elif kind == 'clientuserinfochanged':
                c['name'] = data.get('player_name')
                c['guid'] = data.get('guid')
            elif kind == 'clientbegin':
                c = {}
            elif kind == 'clientdisconnect':
                del state[client_id]


def main(argv):
    args = docopt(__doc__, argv=argv)

    context = zmq.Context()
    in_socket = context.socket(zmq.SUB)
    in_socket.connect(args['--context-socket'])

    filters = ['initgame', 'shutdowngame', 'clientdisconnect',
               'clientbegin', 'clientuserinfochanged', 'hit', 'kill']
    add_filter = partial(in_socket.setsockopt, zmq.SUBSCRIBE)
    map(add_filter, filters)

    update_ledbar(in_socket)
