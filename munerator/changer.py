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
import re
import time
from functools import partial

import zmq
from docopt import docopt
from Levenshtein import ratio


log = logging.getLogger(__name__)
voting_enabled = False


class Changer(object):
    def __init__(self, in_socket, rcon_socket):
        self.in_socket = in_socket
        self.rcon_socket = rcon_socket
        self.votecache = []

    def rcon(self, cmd):
        self.rcon_socket.send_string(cmd)
        response = self.rcon_socket.recv_string()
        log.debug('cmd:%s response:%s' % (cmd, str(response)))

    def rcon_get_value(self, value):
        self.rcon_socket.send_string(value)
        try:
            response = json.loads(self.rcon_socket.recv_string())
            assert len(response) == 2
        except:
            log.error('invalid response')
            return None

        m = re.match('"%s" is:"(?P<value>[^\^]*)\^7".*' % value, response[1])
        if m:
            return m.group('value')
        else:
            return None

    def change(self):
        while True:
            kind, data = self.in_socket.recv_string().split(' ', 1)
            log.debug('got %s: %s' % (kind, data))
            data = json.loads(data)

            if kind == 'initgame':
                # reset votecache on game start
                self.votecache = []
            elif kind in ['clientbegin', 'clientdisconnect']:
                fraglimit = int(self.rcon_get_value('fraglimit'))
                num_players = len(data.get('game_info', {}).get('clients', {}))

                # increate fraglimit by 8 for every two players joining
                new_fraglimit = int(num_players) / 2 * 8
                new_fraglimit = new_fraglimit = max(10, min(new_fraglimit, 30))

                log.debug('fraglimit:%s new_fraglimit:%s' % (fraglimit, new_fraglimit))

                if new_fraglimit > fraglimit:
                    log.info('new fraglimit %s' % new_fraglimit)
                    self.rcon('set fraglimit %s' % new_fraglimit)
            elif voting_enabled and kind == 'say':
                self.voting(data)

    def voting(self, data):
        text = data.get('text')

        if ratio(text, u'instagib') > 0.75:
            change = ('gametype', 'instagib')
        elif ratio(text, u'again') > 0.75:
            change = ('map', 'restart')
        else:
            return

        client_id = data.get('client_id')
        self.record_vote(client_id, change)

        num_players = len(data.get('game_info', {}).get('clients', {}))
        votes = self.votes_for_change(change)
        log.info('votes:%s num_players:%s' % (votes, num_players))
        if votes >= num_players / 2:
            changetype, value = change
            for i in range(4):
                self.rcon('say got %s votes for %s %s, changing game!' % (votes, changetype, value))
                time.sleep(1)
            self.apply_change(change)
        else:
            votes_needed = (num_players / 2) - votes
            changetype, value = change
            self.rcon('say need %s more votes for %s %s' % (votes_needed, changetype, value))

    def apply_change(self, change):
        changetype, value = change
        if changetype == 'gametype':
            self.change_gametype(value)
        elif changetype == 'map' and value == 'restart':
            self.change_gametype('')

    def record_vote(self, client_id, change):
        vote = (client_id, change)
        self.votecache.append(vote)

    def votes_for_change(self, change):
        votes = []
        for client_id, change_vote in self.votecache:
            if change == change_vote:
                if client_id not in votes:
                    votes.append(client_id)
        return len(votes)

    def change_gametype(self, gametype):
        nextmap = self.rcon_get_value('nextmap')

        self.rcon('set g_rockets 0')
        self.rcon('set g_instantgib 0')

        if gametype == 'instagib':
            self.rcon('set g_instantgib 2')
        elif gametype == 'rockets':
            self.rcon('set g_rockets 1')

        self.rcon('map_restart')
        time.sleep(2)
        self.rcon('set nextmap %s' % nextmap)


def main(argv):
    args = docopt(__doc__, argv=argv)

    context = zmq.Context()

    in_socket = context.socket(zmq.SUB)
    in_socket.connect(args['--context-socket'])

    filters = ['initgame', 'clientbegin', 'clientdisconnect', 'say']
    add_filter = partial(in_socket.setsockopt, zmq.SUBSCRIBE)
    map(add_filter, filters)

    rcon_socket = context.socket(zmq.PUB)
    rcon_socket.connect(args['--rcon-socket'])

    c = Changer(in_socket, rcon_socket)
    c.change()
