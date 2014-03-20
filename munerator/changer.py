"""Change aspects about the current game

Usage:
  munerator [options] changer

Options:
  -v --verbose          Verbose logging
  --context-socket url  ZMQ socket for context events [default: tcp://quake.brensen.com:9002]
  --rcon-socket url     ZMQ socket for rcon commands [default: tcp://127.0.0.1:9005]

"""
import json
import logging
import time
from functools import partial

import zmq
from docopt import docopt

log = logging.getLogger(__name__)


def change(in_socket, rcon_socket):
    while True:
        kind, data = in_socket.recv_string().split(' ', 1)
        log.debug('got %s: %s' % (kind, data))
        data = json.loads(data)

        if kind == 'initgame':
            time.sleep(10)
            rcon_socket.send_string('say munerator is watching')
            response = rcon_socket.recv_string()
            log.debug('response: %s' % str(response))


def main(argv):
    args = docopt(__doc__, argv=argv)

    context = zmq.Context()

    in_socket = context.socket(zmq.SUB)
    in_socket.connect(args['--context-socket'])

    filters = ['initgame']
    add_filter = partial(in_socket.setsockopt, zmq.SUBSCRIBE)
    map(add_filter, filters)

    rcon_socket = context.socket(zmq.REQ)
    rcon_socket.connect(args['--rcon-socket'])

    change(in_socket, rcon_socket)
