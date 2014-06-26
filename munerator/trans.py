"""Translate events

Usage:
  munerator [options] trans

Options:
  -v --verbose         Verbose logging
  --raw-socket url     ZMQ socket for raw logline [default: tcp://127.0.0.1:9000]
  --events-socket url  ZMQ socket for raw events [default: tcp://127.0.0.1:9001]

"""
from docopt import docopt
import zmq
import logging
log = logging.getLogger(__name__)

import re


translaters = [
    (r'[0-9: ]*InitGame: .*\\mapname\\(?P<mapname>[\w]+).*', 'initgame'),
    (r'[0-9: ]*ShutdownGame:.*', 'shutdowngame'),
    (r'[0-9: ]*say: (?P<player_name>[^:]+): (?P<text>.+)', 'say'),
    (r'[0-9: ]*ClientUserinfoChanged: (?P<client_id>\d+) n\\(?P<player_name>[^\\]+)\\t\\(?P<team_id>\d+).*id\\'
        r'(?P<guid>[\w]+)', 'clientuserinfochanged'),
    (r'.*client:(?P<client_id>\d+) health:(?P<health>[\d-]+).*', 'hit'),
    (r'[0-9: ]*Kill: [^:]+: (?P<killer>.+) killed (?P<killed>.+) by (?P<mod>[\w]+)', 'kill'),
    (r'[0-9: ]*ClientDisconnect: (?P<client_id>\d+)', 'clientdisconnect'),
    (r'[0-9: ]*ClientConnect: (?P<client_id>\d+)', 'clientconnect'),
    (r'[0-9: ]*ClientBegin: (?P<client_id>\d+)', 'clientbegin'),
    (r'[0-9: ]*PlayerScore: (?P<client_id>\d+) (?P<score>[\d\-]):.*', 'playerscore'),
    (r'[0-9: ]*Item: (?P<client_id>\d+) item_quad.*', 'quad'),
    (r'[0-9: ]*ClientUserinfoChanged: (?P<guid>(?P<client_id>\d+)) n\\(?P<player_name>[^\\]+)\\t\\(?P<team_id>\d+).*'
        r'\\skill\\ (?P<skill>[\d\.]+).*id\\', 'clientuserinfochanged'),
]

regexes = [(re.compile(r), k) for r, k in translaters]


def translate(line, regexes):
    for regex, kind in regexes:
        m = regex.match(line)
        if m:
            yield kind, m.groupdict()


def handle_line(ts, line, out_socket):
    for kind, data in translate(line, regexes):
        data['kind'] = kind
        log.debug('out: %s' % data)
        break
    else:
        data = {
            'kind': 'unhandled',
            'raw': line
        }

    data['timestamp'] = ts
    out_socket.send_json(data)


def eventstream(in_socket, out_socket):
    while True:
        msg = in_socket.recv_string()
        ts, line = msg.split(' ', 1)

        log.debug('translating: ' + line)

        handle_line(ts, line, out_socket)


def main(argv):
    args = docopt(__doc__, argv=argv)

    context = zmq.Context()
    in_socket = context.socket(zmq.PULL)
    in_socket.bind(args['--raw-socket'])

    out_socket = context.socket(zmq.PUSH)
    out_socket.connect(args['--events-socket'])

    eventstream(in_socket, out_socket)
