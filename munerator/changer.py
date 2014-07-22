"""Change aspects about the current game

Usage:
  munerator [options] changer

Options:
  -v --verbose          Verbose logging
  --context-socket url  ZMQ socket for context events [default: tcp://quake.brensen.com:9002]
  --rcon-socket url     ZMQ socket for rcon commands [default: tcp://127.0.0.1:9005]
  --database ip:port    Host and port for mongo database [default: 127.0.0.1:27017]

"""
import logging
from functools import partial

import zmq
from docopt import docopt
from munerator.common.eventler import Eventler
from munerator.common.database import setup_eve_mongoengine
from munerator.games import Game
from munerator.mapreduce import Playlister, VoteReduce


log = logging.getLogger(__name__)


class Changer(Eventler):
    def __init__(self, *args, **kwargs):
        super(Changer, self).__init__(*args, **kwargs)
        self.playlister = Playlister()
        self.votereduce = VoteReduce()
        self.update_playlist()

    def rcon(self, cmd):
        self.rcon_socket.send_string(cmd)

    def handle_event(self, kind, data):
        """
        Apply changes based on gameplay event. Eg. player joins -> increase fraglimit
        """

        if kind in ['clientbegin', 'clientdisconnect']:
            self.update_fraglimit(data)
            self.update_playlist()

        if kind in ['initgame']:
            self.update_playlist()

    def update_playlist(self):
        # update player votes and generate new playlist
        if hasattr(self, 'db'):
            self.votereduce.vote_reduce()
            self.playlister.generate_playlist()

    def update_fraglimit(self, data):
        fraglimit = data.get('game_info', {}).get('fraglimit')
        num_players = data.get('game_info', {}).get('num_players')

        if all([fraglimit, num_players]):
            new_fraglimit = Game.get_fraglimit(num_players)
            log.debug('fraglimit:%s new_fraglimit:%s' % (fraglimit, new_fraglimit))

            if new_fraglimit > fraglimit:
                log.info('new fraglimit %s' % new_fraglimit)
                self.rcon('set fraglimit %s' % new_fraglimit)


def main(argv):
    args = docopt(__doc__, argv=argv)

    context = zmq.Context()

    in_socket = context.socket(zmq.SUB)
    in_socket.connect(args['--context-socket'])

    filters = ['clientbegin', 'clientdisconnect', 'initgame']
    add_filter = partial(in_socket.setsockopt, zmq.SUBSCRIBE)
    map(add_filter, filters)

    rcon_socket = context.socket(zmq.PUSH)
    rcon_socket.connect(args['--rcon-socket'])

    # setup database
    host, port = args['--database'].split(':')
    db = setup_eve_mongoengine(host, port)

    c = Changer(in_socket, rcon_socket=rcon_socket, db=db)
    c.handle_events()
