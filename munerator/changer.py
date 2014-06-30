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
from functools import partial

import zmq
from docopt import docopt


log = logging.getLogger(__name__)


class Changer(object):

    def __init__(self, in_socket, rcon_socket):
        self.in_socket = in_socket
        self.rcon_socket = rcon_socket

    def rcon(self, cmd):
        self.rcon_socket.send_string(cmd)

    def change(self):
        """
        Apply changes based on gameplay event. Eg. player joins -> increase fraglimit
        """
        while True:
            kind, data = self.in_socket.recv_string().split(' ', 1)
            log.debug('got %s: %s' % (kind, data))
            data = json.loads(data)

            self.handle_event(kind, data)

    def handle_event(self, kind, data):
        if kind in ['clientbegin', 'clientdisconnect']:
            fraglimit = data.get('game_info', {}).get('fraglimit')
            num_players = data.get('game_info', {}).get('num_players')

            if all([fraglimit, num_players]):
                # increate fraglimit by 8 for every two players joining
                new_fraglimit = int(num_players) / 2 * 8
                new_fraglimit = new_fraglimit = max(10, min(new_fraglimit, 30))

                log.debug('fraglimit:%s new_fraglimit:%s' % (fraglimit, new_fraglimit))

                if new_fraglimit > fraglimit:
                    log.info('new fraglimit %s' % new_fraglimit)
                    self.rcon('set fraglimit %s' % new_fraglimit)


def main(argv):
    args = docopt(__doc__, argv=argv)

    context = zmq.Context()

    in_socket = context.socket(zmq.SUB)
    in_socket.connect(args['--context-socket'])

    filters = ['clientbegin', 'clientdisconnect']
    add_filter = partial(in_socket.setsockopt, zmq.SUBSCRIBE)
    map(add_filter, filters)

    rcon_socket = context.socket(zmq.PUSH)
    rcon_socket.connect(args['--rcon-socket'])

    c = Changer(in_socket, rcon_socket)
    c.change()
