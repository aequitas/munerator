"""Listen and output game event

Usage:
  munerator [options] listen [<event>...]

Options:
  -v --verbose          Verbose logging
  --context-socket url  ZMQ socket for context events [default: tcp://quake.brensen.com:9002]

"""
import json
import logging

import zmq
from docopt import docopt
from functools import partial


log = logging.getLogger(__name__)

exclude_keys = ['kind', 'timestamp']


def listen(in_socket, show_context=False):
    log.info('listening for game events')
    while True:
        msg = in_socket.recv_string()

        log.debug('got: %s' % msg)
        data = json.loads(msg.split(' ', 1)[-1])
        kind = data.get('kind')

        print(kind, ' '.join(['%s:%s' % (k, v) for k, v in data.items() if k not in exclude_keys]))


def main(argv):
    args = docopt(__doc__, argv=argv)

    context = zmq.Context()
    in_socket = context.socket(zmq.SUB)
    in_socket.connect(args['--context-socket'])

    if args['<event>']:
        log.debug('filters: %s' % ', '.join(args['<event>']))
        add_filter = partial(in_socket.setsockopt, zmq.SUBSCRIBE)
        map(add_filter, args['<event>'])
    else:
        in_socket.setsockopt(zmq.SUBSCRIBE, '')

    listen(in_socket)
