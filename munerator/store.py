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
from mongoengine import connect
from munerator.common.models import Games, Players, Votes

log = logging.getLogger(__name__)


def handle_events(in_socket, rcon_socket):
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
            handle_event(kind, data, rcon_socket)
        except:
            log.exception('error in event handling')


def handle_event(kind, data, rcon_socket):
    """
    Parse event message and update database with new information.
    """

    # get player and/or game id from data
    player_id = str(data.get('client_info', {}).get('guid', ''))
    game_id = str(data.get('game_info', {}).get('id', ''))

    player, new = Players.objects.get_or_create(guid=player_id)
    if new:
        player.save()
    game, new = Games.objects.get_or_create(game_id=game_id)
    if new:
        game.save()

    # handle player updates
    if player and kind in ['clientbegin', 'clientdisconnect', 'clientuserinfochanged', 'playerscore']:
        if new:
            log.debug('creating new player')

        # on name change, store previous name
        if data['client_info'] and player.name != data['client_info']['name']:
            player.update(add_to_set__names=data['client_info']['name'])

        # update variable data
        player.update(**{'set__%s' % k: v for k, v in data['client_info'].items() if not k.endswith('id')})

        # add player to game
        if game_id:
            game, new = Games.objects.get_or_create(game_id=game_id)
            game.update(add_to_set__players=player)

        log.info('updated player')

    # handle game updates
    if game and kind in ['initgame', 'shutdowngame']:
        if new:
            log.debug('creating new game')
            game.game_id = game_id

        # update variable data
        game.update(**{'set__%s' % k: v for k, v in data['game_info'].items()if not k.endswith('id')})

        log.info('updated game')

    # handle votes
    if kind == 'say' and player and game:
        if data.get('text') in ['+1', 'gg', 'GG', 'GGG', 'like', 'fuckthismaprocks', '++', '+1337']:
            vote = Votes(player=player, game=game, vote=1)
        elif data.get('text') in ['-1', '--1', '-11', '-1000', '-2', 'dislike', 'hate', 'RAGE!!!', 'fuckthismap', '--']:
            vote = Votes(player=player, game=game, vote=-1)
        vote.save()
        rcon_socket.send_string('say %s your vote has been counted' % player.name)
        log.info('saved vote')


def main(argv):
    args = docopt(__doc__, argv=argv)

    # setup zmq input socket
    context = zmq.Context()
    in_socket = context.socket(zmq.SUB)
    in_socket.connect(args['--context-socket'])
    in_socket.setsockopt(zmq.SUBSCRIBE, '')

    # apply message filters
    filters = [
        'initgame', 'shutdowngame', 'clientdisconnect', 'say',
        'clientbegin', 'clientuserinfochanged', 'playerscore'
    ]
    add_filter = partial(in_socket.setsockopt, zmq.SUBSCRIBE)
    map(add_filter, filters)

    # setup rcon socket
    rcon_socket = context.socket(zmq.PUB)
    rcon_socket.connect(args['--rcon-socket'])

    # setup database
    host, port = args['--database'].split(':')
    connect('munerator', host=host, port=int(port))

    # start event loop
    handle_events(in_socket, rcon_socket)
