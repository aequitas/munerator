"""Display game events on ledbar

Usage:
  munerator [options] ledbar

Options:
  -v --verbose          Verbose logging
  --context-socket url  ZMQ socket for context events [default: tcp://quake.brensen.com:9002]
  --ledbar-api url      URL to ledbar api [default: http://10.110.0.119/led/{led}/{color_code}]
  --numleds num         Number of leds in the bar to use [default: 19]

"""
import collections
import itertools
import json
import logging
import urllib2
from functools import partial

import zmq
from docopt import docopt
from webcolors import name_to_hex

log = logging.getLogger(__name__)


class Ledbar(object):
    def __init__(self, numleds, ledbar_api):
        self.prev_state = ['#000000'] * numleds
        self.ledbar_api = ledbar_api
        self.numleds = numleds

    def api_call(self, url):
        try:
            urllib2.urlopen(url, timeout=0.5)
        except:
            log.debug('urlopen failed')

    def update_leds(self, state):
        for i, color in enumerate(state):
            if not color.startswith('#'):
                color = name_to_hex(color)

            if color != self.prev_state[i]:
                led = self.numleds - (i + 1)
                color_code = color.lstrip('#')

                url = self.ledbar_api.format(led=led, color_code=color_code)
                log.debug('url: %s' % url)
                self.api_call(url)

            self.prev_state[i] = color


def update_ledbar(in_socket, numleds, ledbar):
    ids = None

    while True:
        msg = in_socket.recv_string()

        log.debug('got : %s' % msg)
        data = json.loads(msg.split(' ', 1)[-1])
        kind = data.get('kind')
        client_id = data.get('client_id', '')

        if kind == 'initgame' or ids is None:
            ids = collections.defaultdict(itertools.count().next)
            num_players = data.get('game_info', {}).get('num_players', 0)
            state = ['white'] * num_players + ['black'] * (numleds - num_players)
        elif client_id.isdigit() and int(client_id) < numleds:
            s = state[ids[int(client_id)]]
            if kind == 'clientbegin':
                team = data.get('game_info', {}).get('clients', {}).get(client_id, {}).get('team')
                if team and team in ['red', 'blue']:
                    s = team
                else:
                    s = 'white'
            elif kind == 'hit':
                if s in ['cyan', 'invisible']:
                    continue
                health = int(data.get('health'))
                if health < 50:
                    s = 'orange'
                elif health < 25:
                    s = 'orangered'
            elif kind == 'quad':
                s = 'cyan'
            elif kind == 'invisible':
                s = 'black'
            elif kind == 'clientdisconnect':
                s = '#212121'
            state[ids[int(client_id)]] = s
        elif kind == 'kill':
            c = data.get('clients', {})
            killer_id = [k for k, v in c.items() if v.get('name') == data.get('killer')]
            killed_id = [k for k, v in c.items() if v.get('name') == data.get('killed')]

            if killer_id:
                state[ids[int(killer_id[0])]] = 'green'
            if killed_id:
                state[ids[int(killed_id[0])]] = 'red'

        ledbar.update_leds(state)


def main(argv):
    args = docopt(__doc__, argv=argv)

    context = zmq.Context()
    in_socket = context.socket(zmq.SUB)
    in_socket.connect(args['--context-socket'])

    filters = ['initgame', 'shutdowngame', 'clientdisconnect', 'quad',
               'clientbegin', 'clientuserinfochanged', 'hit', 'kill']
    add_filter = partial(in_socket.setsockopt, zmq.SUBSCRIBE)
    map(add_filter, filters)

    numleds = int(args['--numleds'])
    ledbar_api = args['--ledbar-api']

    ledbar = Ledbar(numleds, ledbar_api)

    update_ledbar(in_socket, numleds, ledbar)
