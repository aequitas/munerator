"""Display game events on ledbar

Usage:
  munerator [options] ledbar

Options:
  -v --verbose          Verbose logging
  --context-socket url  ZMQ socket for context events [default: tcp://quake.brensen.com:9002]

"""
import collections
import itertools
import json
import logging
import time
import urllib2
from functools import partial

import zmq
from docopt import docopt
from webcolors import name_to_hex

log = logging.getLogger(__name__)


def update_leds(state, numleds):
    prev_state = [''] * numleds
    while True:
        for i, color in enumerate(state):
            if color != prev_state[i]:
                led = numleds - i
                color_code = name_to_hex(color)
                try:
                    urllib2.urlopen('http://ijohan.nl/led/%s/%s' % (led, color_code), timeout=0.1)
                except:
                    log.debug('urlopen failed')
            prev_state[i] = color
        yield

def update_ledbar(in_socket, numleds):
    ids = None

    while True:
        t = int(time.time())
        msg = in_socket.recv_string()

        # log.debug('got : %s' % msg)
        data = json.loads(msg.split(' ', 1)[-1])
        kind = data.get('kind')
        client_id = data.get('client_id')

        if kind == 'initgame' or ids is None:
            ids = collections.defaultdict(itertools.count().next)
            state = ['black'] * numleds
        elif client_id and client_id < numleds:
            s = state[ids[client_id]]
            if kind == 'clientbegin':
                s = 'white'
            elif kind == 'clientdisconnect':
                s = 'grey'
            state[ids[client_id]] = s
        elif kind == 'kill':
            c = data.get('game_info', {}).get('clients', {})
            killer_id = [k for k,v in c.items() if v.get('name') == data.get('killer')]
            killed_id = [k for k,v in c.items() if v.get('name') == data.get('killed')]

            if killer_id:
                state[int(killer_id[0])] = 'green'
            if killed_id:
                state[int(killed_id[0])] = 'red'

        log.debug(state)
        update_leds(state, numleds)


def main(argv):
    args = docopt(__doc__, argv=argv)

    context = zmq.Context()
    in_socket = context.socket(zmq.SUB)
    in_socket.connect(args['--context-socket'])

    filters = ['initgame', 'shutdowngame', 'clientdisconnect',
               'clientbegin', 'clientuserinfochanged', 'hit', 'kill']
    add_filter = partial(in_socket.setsockopt, zmq.SUBSCRIBE)
    map(add_filter, filters)

    update_ledbar(in_socket, 19)
