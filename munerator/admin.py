"""Perform admin commands like merging players.

Usage:
  munerator [options] admin merge_players [<player_id> ...]

Options:
  -v --verbose          Verbose logging
  --database ip:port    Host and port for mongo database [default: 127.0.0.1:27017]

"""
import logging

from docopt import docopt
from munerator.common.database import setup_eve_mongoengine
from munerator.common.models import Players, Votes, Games

log = logging.getLogger(__name__)


def merge_players(player_ids):
    players = list(Players.objects(id__in=player_ids).order_by('last_seen'))

    merge_into = players.pop()
    log.info('last seen player is: {0.name}({0.id}, {0.guids}, {0.names})'.format(merge_into))
    log.info('current player votes/games: %s %s' % (
        len(Votes.objects(player=merge_into.id)),
        len(Games.objects(players=merge_into.id))
    ))
    for player in players:
        log.info('merging {0.name}({0.id}, {0.guids}, {0.names})'.format(player))

        votes = Votes.objects(player=player.id)
        log.info('updating %s votes' % len(votes))
        votes.update(set__player=merge_into.id)

        games = Games.objects(players=player.id)
        log.info('updating %s games' % len(games))
        games.update(add_to_set__players=merge_into.id)
        games.update(pull__players=player.id)

        for guid in player.guids:
            merge_into.update(add_to_set__guids=guid)
        for name in player.names:
            merge_into.update(add_to_set__names=name)

        log.info('removing player: %s' % player.id)
        player.delete()

    log.info('new player info: {0.name}({0.id}, {0.guids}, {0.names})'.format(merge_into))
    log.info('new player votes/games: %s/%s' % (
        len(Votes.objects(player=merge_into.id)),
        len(Games.objects(players=merge_into.id))
    ))


def list_mergable_players():
    for player in Players.objects:
        print player.id, ", ".join(player.names)


def main(argv):
    args = docopt(__doc__, argv=argv)

    # setup database
    host, port = args['--database'].split(':')
    setup_eve_mongoengine(host, port)

    if args['merge_players']:
        if args['<player_id>']:
            merge_players(args['<player_id>'])
        else:
            list_mergable_players()
