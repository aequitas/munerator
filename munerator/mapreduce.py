"""
Reduce map into a playlist of most populair games to be played based current player votes, num. players, etc.
"""

from munerator.common.database import setup_eve_mongoengine

import logging
import datetime
# from bson.objectid import ObjectId
from bson.code import Code
from bson.son import SON

log = logging.getLogger(__name__)


def populate_playlist(db):
    # online player ids and online plyaer count
    online_players = [p['_id'] for p in db.players.find({"online": True}, fields='_id')]
    online_player_count = len(online_players)
    # normalized to value between 2-16
    normalized_count = min(16, max(2, online_player_count))
    log.debug('map search player count: %s' % normalized_count)

    not_updated_after = datetime.datetime.today() - datetime.timedelta(hours=1)

    maps_map = Code("""
    function maps_map() {
        var key = {
            gametype: null,
            gamemap:this._id
        };
        var value = {
            gamemap: this._id,
            gametype: 0,
            score: 0,
            votes: []
        };
        // emit for every map/playlist combination
        this.gametypes.forEach(function(gametype){
            value.gametype = gametype;
            key.gametype = gametype;
            emit(key, value);
        });
    }
    """)

    votes_map = Code("""
    function(){
        var key = {
            gametype: this.gametype,
            gamemap: this.gamemap
        };
        var value = {
            gamemap: this.gamemap,
            gametype: this.gametype,
            score: this.vote,
            votes: [this._id],
        };
        emit(key, value);
    }
    """)

    sum_score = Code("""
    function(key, values){
        var reduced_value = {
            gamemap: key.gamemap,
            gametype: key.gametype,
            score: 0,
            votes: []
        };
        var scores = [];
        var votes = [];
        values.forEach(function(value){
            votes = votes.concat(value.votes);
            scores.push(value.score);
        });
        reduced_value.score = Array.sum(scores);
        reduced_value.votes = votes;

        return reduced_value;
    }
    """)

    map_query = {}
    {
        "min_players": {"$lte": normalized_count},
        "max_players": {"$gte": normalized_count},
        "$or": [
            {"last_played": {"$lte": not_updated_after}},
            {"last_played": {"$exists": False}}
        ]
    }

    vote_query = {
        "player": {"$in": online_players}
    }

    # prime results with maps suiting for current players
    out = SON([("replace", "reduced")])
    mr_out = db.gamemaps.map_reduce(maps_map, sum_score, out, map_query)
    log.debug('maps mapreduce output: %s', mr_out)

    # merge vote scores onto maps
    out = SON([("merge", "reduced")])
    mr_out = db.votes.map_reduce(votes_map, sum_score, out, vote_query)
    log.debug('votes mapreduce output: %s', mr_out)

    db.playlist_items.remove({})
    db.playlist_items.insert([r.get('value') for r in db.reduced.find({'value.score': {'$gte': 0}})])
    log.debug('nr. playlist items: %s', db.playlist_items.count())


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    db = setup_eve_mongoengine()
    populate_playlist(db)
