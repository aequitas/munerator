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
        self.prev_state = [''] * numleds
        self.ledbar_api = ledbar_api
        self.numleds = numleds

    def api_call(self, url):
        try:
            urllib2.urlopen(url, timeout=0.5)
        except:
            log.debug('urlopen failed')

    def update_leds(self, state):
        for i, color in enumerate(state):
            if color != self.prev_state[i]:
                led = self.numleds - (i + 1)
                color_code = name_to_hex(color).lstrip('#')

                url = self.ledbar_api.format(led=led, color_code=color_code)
                log.debug('url: %s' % url)
                self.api_call(url)

            self.prev_state[i] = color


def update_ledbar(in_socket, numleds, ledbar_api):
    ids = None

    ledbar = Ledbar(numleds, ledbar_api)

    while True:
        msg = in_socket.recv_string()

        log.debug('got : %s' % msg)
        data = json.loads(msg.split(' ', 1)[-1])
        kind = data.get('kind')
        client_id = data.get('client_id', '')

        if kind == 'initgame' or ids is None:
            ids = collections.defaultdict(itertools.count().next)
            state = ['black'] * numleds
        elif client_id.isdigit() and int(client_id) < numleds:
            s = state[ids[int(client_id)]]
            if kind == 'clientbegin':
                s = 'white'
            elif kind == 'hit':
                if s in ['blue']:
                    continue
                s = 'orange'
            elif kind == 'quad':
                s = 'blue'
            elif kind == 'clientdisconnect':
                s = 'dimgray'
            state[ids[int(client_id)]] = s
        elif kind == 'kill':
            c = data.get('game_info', {}).get('clients', {})
            killer_id = [k for k, v in c.items() if v.get('name') == data.get('killer')]
            killed_id = [k for k, v in c.items() if v.get('name') == data.get('killed')]

            if killer_id:
                state[ids[int(killer_id[0])]] = 'green'
            if killed_id:
                state[ids[int(killed_id[0])]] = 'red'

        log.debug(state)
        ledbar.update_leds(state)


def main(argv):
    args = docopt(__doc__, argv=argv)

    context = zmq.Context()
    in_socket = context.socket(zmq.SUB)
    in_socket.connect(args['--context-socket'])

    filters = ['initgame', 'shutdowngame', 'clientdisconnect',
               'clientbegin', 'clientuserinfochanged', 'hit', 'kill']
    add_filter = partial(in_socket.setsockopt, zmq.SUBSCRIBE)
    map(add_filter, filters)

    numleds = int(args['--numleds'])
    ledbar_api = args['--ledbar-api']

    update_ledbar(in_socket, numleds, ledbar_api)
