"""Translate events

Usage:
  munerator [options] old

Options:
  -v --verbose          Verbose logging
  --context-socket url  ZMQ socket for context events [default: tcp://quake.brensen.com:9002]
  --old-api url         URL to old API [default: http://quake.ijohan.nl/events]

"""
from docopt import docopt
import zmq
import logging
log = logging.getLogger(__name__)

import urllib2
import json
import socket


def proxy_to_old_api(in_socket, base_url):
    while True:
        kind, data = in_socket.recv_string().split(' ', 1)
        log.debug('got %s: %s' % (kind, data))
        data = json.loads(data)

        if kind == 'say':
            url = '%s/say/%s/%s' % (base_url, data.get('player_name'), data.get('text'))
        elif kind == 'initgame':
            url = '%s/InitGame/%s' % (base_url, data.get('mapname'))

        log.info('calling: %s' % url)
        try:
            response = urllib2.urlopen(url, timeout=3)
            log.debug('response %s' % response)
        except socket.timeout:
            log.debug('timeout')
        except:
            log.error('failed', exc_info=True)


def main(argv):
    args = docopt(__doc__, argv=argv)

    context = zmq.Context()
    in_socket = context.socket(zmq.SUB)
    in_socket.connect(args['--context-socket'])
    in_socket.setsockopt(zmq.SUBSCRIBE, 'say')
    in_socket.setsockopt(zmq.SUBSCRIBE, 'initgame')

    proxy_to_old_api(in_socket, args['--old-api'])
