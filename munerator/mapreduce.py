"""
Reduce map into a playlist of most populair games to be played based current player votes, num. players, etc.
"""

from munerator.common.database import setup_eve_mongoengine

import logging
import datetime

log = logging.getLogger(__name__)


def populate_playlist(db):
    players = [p['_id'] for p in db.players.find({"online": True}, fields='_id')]

    online_player_count = len(players)
    normalized_count = min(16, max(2, online_player_count))
    log.debug('map search player count: %s' % normalized_count)

    not_updated_after = datetime.datetime.today() - datetime.timedelta(hours=1)

    maps = db.gamemaps.find(
        {
            "min_players": {"$lte": normalized_count},
            "max_players": {"$gte": normalized_count},
            "_updated": {"$lte": not_updated_after}
        },
        fields='_id'
    )
    map_ids = [m['_id'] for m in maps]

    db.votes.aggregate([
        {
            "$match": {
                "player": {
                    "$in": players
                },
                "gamemap": {
                    "$in": map_ids
                },
            }
        },
        {
            "$group": {
                "_id": "$gamemap",
                "gamemap": {"$first": "$gamemap"},
                "score": {"$sum": "$vote"},
                "votes": {"$push": "$_id"}
            }
        },
        {
            "$out": "playlist_items"
        }
    ])


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    db = setup_eve_mongoengine()
    populate_playlist(db)
