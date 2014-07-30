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
import random
from functools import partial

import zmq
from docopt import docopt
from munerator.common.eventler import ThrottleEventler
from munerator.common.database import setup_eve_mongoengine
from munerator.games import Game
from munerator.mapreduce import Playlister, VoteReduce, PlaylistItems


log = logging.getLogger(__name__)


class Changer(ThrottleEventler):
    def __init__(self, *args, **kwargs):
        super(Changer, self).__init__(*args, **kwargs)
        self.playlister = Playlister()
        self.votereduce = VoteReduce()

        if hasattr(self, 'db'):
            self.update_playlist()

    def rcon(self, cmd):
        self.rcon_socket.send_string(cmd)

    def handle_event(self, kind, data):
        """
        Apply changes based on gameplay event. Eg. player joins -> increase fraglimit
        """

        if kind == 'clientbegin':
            self.actions['update_fraglimit'] = ((data,), {})

        if kind in ['initgame', 'clientbegin', 'clientdisconnect']:
            num_players = data.get('game_info', {}).get('num_players')

            if hasattr(self, 'db'):
                self.actions['set_next_game'] = ((num_players,), {})

        if kind == 'initgame':
            mapname = data.get('game_info', {}).get('mapname')
            self.actions['announce'] = ((mapname,), {})

    def announce(self, mapname):
        self.rcon('say Loaded map %s, mapvote enabled (+1/-1, like/dislike)' % mapname)

    def update_playlist(self):
        # update player votes and generate new playlist
        self.votereduce.vote_reduce()
        self.playlister.generate_playlist()

    def set_next_game(self, num_players):
        self.update_playlist()

        next_game = PlaylistItems.objects.order_by('-score').first()
        if not next_game:
            log.error('failed to determine next game')
            return

        if next_game.gametype == 0 and random.choice(range(5)) == 0:
            special = 'instagib'
        else:
            special = None

        game = Game(next_game.gamemap.name, next_game.gametype, num_players, special)
        log.info('next game: %s' % str(game))
        self.rcon('say Next game: %s' % str(game))

        nextmap_string = game.nextmapstring()
        log.info('nextmap string: %s' % nextmap_string)
        self.rcon(nextmap_string)

    def update_fraglimit(self, data):
        log.debug('checking fraglimit')
        fraglimit = int(data.get('game_info', {}).get('fraglimit'))
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
