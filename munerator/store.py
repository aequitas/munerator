"""Store game events in database

Usage:
  munerator [options] store

Options:
  -v --verbose            Verbose logging
  --context-socket url    ZMQ socket for conext event [default: tcp://127.0.0.1:9002]
  --database ip:port      Host and port for mongo database [default: 127.0.0.1:27017]
  --rcon-socket url       ZMQ socket for rcon commands [default: tcp://127.0.0.1:9005]

"""
import json
import logging
import datetime
from functools import partial

import zmq
from docopt import docopt
from munerator.common.models import Games, Players, Votes, Gamemaps
from munerator.common.database import setup_eve_mongoengine
from mongoengine.queryset import Q

log = logging.getLogger(__name__)


def handle_events(in_socket, rcon_socket):
    """
    Loop over incoming messages and handle them individually.
    """
    # prime commands for current game info
    rcon_socket.send_string('status')
    rcon_socket.send_string('getstatus')

    handled = 0

    log.info('listening for game events')
    while True:
        msg = in_socket.recv_string()

        log.debug('got: %s' % msg)
        data = json.loads(msg.split(' ', 1)[-1])
        kind = data.get('kind')

        try:
            handle_event(kind, data, rcon_socket)
        except:
            log.exception('error in event handling %s' % msg)

        handled += 1
        if not handled % 100:
            log.info('handled another 100 messages (total %s)' % handled)


def handle_event(kind, data, rcon_socket):
    """
    Parse event message and update database with new information.
    """

    # get player and/or game id from data
    player_id = str(data.get('client_info', {}).get('guid', ''))
    timestamp = str(data.get('game_info', {}).get('timestamp', ''))

    player, new_player = Players.objects.get_or_create(guid=player_id) if player_id else (None, None)
    game, new_game = Games.objects.get_or_create(timestamp=timestamp) if timestamp else (None, None)

    if new_player:
        log.info('added new player %s' % data.get('client_info').get('name'))

    # handle player updates
    if player and kind in ['clientbegin', 'clientdisconnect', 'clientuserinfochanged', 'playerscore', 'clientstatus']:
        # on name change, store previous name
        if data['client_info'] and player.name != data['client_info']['name']:
            player.update(add_to_set__names=data['client_info']['name'])

        # update variable data
        player.update(**{'set__%s' % k: v for k, v in data['client_info'].items() if k in player.update_fields})

        # add player to game
        if game:
            game.update(add_to_set__players=player)

        log.debug('updated player')

    # handle game updates
    if game and (kind in ['initgame', 'shutdowngame', 'getstatus'] or new_game):
        # reset all current games
        if kind == 'initgame':
            Games.objects(current=True).update(set__current=False)

        # update variable data
        game.update(**{'set__%s' % k: v for k, v in data['game_info'].items() if k in game.update_fields})

        # set game map
        gamemap, new = Gamemaps.objects.get_or_create(name=data['game_info']['mapname'])
        if new:
            log.info('added map %s' % gamemap.name)
        game.update(set__gamemap=gamemap)

        # update map played times
        if kind == 'shutdowngame':
            if game.players:
                gamemap.update(inc__times_played=1, set__last_played=datetime.datetime.now())

        # store game extra settings
        if data.get('extras'):
            game.options = data.get('extras')
            game.save()

        log.debug('updated game')

        # reset players online status just to be sure
        Players.objects(Q(online=True) | Q(score__ne=None) | Q(team__ne=None)).update(
            set__online=False, set__score=None, set__team=None)

    # handle votes
    if kind == 'say' and player and game:
        vote = None
        if data.get('text') in ['+1', 'gg', 'GG', 'GGG', 'like', 'fuckthismaprocks', '++', '+1337']:
            vote = 1
        elif data.get('text') in ['-1', '--1', '-11', '-1000', '-2', 'dislike', 'hate', 'RAGE!!!', 'fuckthismap', '--']:
            vote = -1

        if vote:
            vote_obj = Votes(player=player, game=game, gamemap=game.gamemap, gametype=game.gametype, mapname=game.gamemap.name, vote=vote)
            rcon_socket.send_string('say %s^7 your vote has been counted' % player.name)
            vote_obj.save()
            log.info('saved vote')

            # add vote to game
            game.update(add_to_set__votes=vote_obj)


def main(argv):
    args = docopt(__doc__, argv=argv)

    # setup zmq input socket
    context = zmq.Context()
    in_socket = context.socket(zmq.SUB)
    in_socket.connect(args['--context-socket'])

    # apply message filters
    filters = [
        'initgame', 'shutdowngame', 'clientdisconnect', 'say',
        'clientbegin', 'clientuserinfochanged', 'playerscore'
    ]
    add_filter = partial(in_socket.setsockopt, zmq.SUBSCRIBE)
    map(add_filter, filters)

    # setup rcon socket
    rcon_socket = context.socket(zmq.PUSH)
    rcon_socket.connect(args['--rcon-socket'])

    # setup database
    host, port = args['--database'].split(':')
    setup_eve_mongoengine(host, port)

    # start event loop
    handle_events(in_socket, rcon_socket)
