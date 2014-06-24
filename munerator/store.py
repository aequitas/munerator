"""Store game events in database

Usage:
  munerator [options] store

Options:
  -v --verbose            Verbose logging
  --context-socket url    ZMQ socket for conext event [default: tcp://127.0.0.1:9002]
  --database ip:port      Host and port for mongo database [default: 127.0.0.1:27017]

"""
import json
import logging
from functools import partial

import zmq
from docopt import docopt
from mongokit import Connection, Document

log = logging.getLogger(__name__)


class Player(Document):
    __collection__ = 'players'
    __database__ = 'munerator'
    structure = {
        'id': bytes,
        'name': bytes,
        'names': [bytes],
    }
    default_values = {
        'names': list(),
    }


class Game(Document):
    __collection__ = 'games'
    __database__ = 'munerator'
    structure = {
        'id': int,
        'mapname': bytes,
        'players': [bytes],
        'state': bytes,
        'start': bytes,
        'stop': bytes,
    }
    default_values = {
        'players': list(),
    }


def handle_events(in_socket, database):
    """
    Loop over incoming messages and handle them individually.
    """
    log.info('listening for game events')
    while True:
        msg = in_socket.recv_string()

        log.debug('got: %s' % msg)
        data = json.loads(msg.split(' ', 1)[-1])
        kind = data.get('kind')

        try:
            handle_event(kind, data, database=database)
        except:
            log.exception('error in event handling')


def handle_event(kind, data, database):
    """
    Parse event message and update database with new information.
    """

    # get player and/or game id from data
    player_id = data.get('client_info', {}).get('guid')
    game_id = data.get('game_info', {}).get('id')

    # handle player updates
    if player_id and kind in ['clientbegin', 'clientdisconnect', 'clientuserinfochanged', 'playerscore']:
        player = database.Player.find_one({'id': player_id})
        if not player:
            log.debug('creating new player')
            player = database.Player()
            player['id'] = data['client_info']['guid']

        # on name change, store previous name
        if player['name'] != data['client_info']['name']:
            player['names'].append(data['client_info']['name'])

        # update variable data
        player['name'] = data['client_info']['name']

        player.save()

        # add player to game
        game = database.Game.find_one({'id': game_id})
        if game and player['id'] not in game['players']:
            game['players'].append(player['id'])
            game.save()

        log.info('updated player')

    # handle game updates
    if game_id and kind in ['initgame', 'shutdowngame']:
        game = database.Game.find_one({'id': game_id})
        if not game:
            log.debug('creating new game')
            game = database.Game()
            game['id'] = data['game_info']['id']
            game['mapname'] = data['game_info']['mapname']
            game['start'] = data['game_info']['start']

        # update current game state
        if kind == 'initgame':
            game['state'] = 'current'
        elif kind == 'shutdowngame':
            game['state'] = 'played'
            game['stop'] = data['game_info']['stop']

        game.save()

        log.info('updated game')


def main(argv):
    args = docopt(__doc__, argv=argv)
    log.info('test')

    context = zmq.Context()
    in_socket = context.socket(zmq.SUB)
    in_socket.connect(args['--context-socket'])

    in_socket.setsockopt(zmq.SUBSCRIBE, '')

    filters = [
        'initgame', 'shutdowngame', 'clientdisconnect',
        'clientbegin', 'clientuserinfochanged', 'playerscore'
    ]
    add_filter = partial(in_socket.setsockopt, zmq.SUBSCRIBE)
    map(add_filter, filters)

    host, port = args['--database'].split(':')
    connection = Connection(host, int(port))
    connection.register([Player, Game])

    database = connection.munerator

    handle_events(in_socket, database)
