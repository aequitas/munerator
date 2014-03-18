"""Store live data in shelve

Usage:
  munerator [options] live

Options:
  -v --verbose      Verbose logging
  --context-socket  ZMQ socket for conext event [default: tcp://127.0.0.1:9002]

"""
from docopt import docopt
import zmq
import logging
log = logging.getLogger(__name__)

from functools import partial
import shelve
import json


def update_live(in_socket, db_file):
    while True:
        kind, data = in_socket.recv_string().split(' ', 1)
        data = json.loads(data)
        client_id = data.get('client_id')

        db = shelve.open(filename=db_file, flag='c')

        if client_id:
            clients = db.get('clients', {})
            if not client_id in clients:
                clients[client_id] = {}
            c = clients[client_id]

            if kind == 'hit':
                c['health'] = data.get('health')
            elif kind == 'playerscore':
                c['score'] = data.get('score')
            elif kind == 'clientuserinfochanged':
                c['name'] = data.get('player_name')
                c['guid'] = data.get('guid')
            elif kind == 'clientbegin':
                c = {}
            elif kind == 'clientdisconnect':
                del clients[client_id]

            db['clients'] = clients

        if kind == 'initgame':
            db['game'] = {
                'mapname': data.get('mapname')
            }
            db['clients'] = {}
        elif kind == 'shutdowngame':
            db['game'] = {}
            db['clients'] = {}

        db.close()


def main(argv):
    args = docopt(__doc__, argv=argv)

    context = zmq.Context()
    in_socket = context.socket(zmq.SUB)
    in_socket.connect(args['--context-socket'])

    filters = ['initgame', 'shutdowngame', 'clientdisconnect', 'clientbegin', 'clientuserinfochanged', 'hit']
    add_filter = partial(in_socket.setsockopt, zmq.SUBSCRIBE)
    map(add_filter, filters)

    update_live(in_socket, args['--db-file'])
