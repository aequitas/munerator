"""
Reduce map into a playlist of most populair games to be played based current player votes, num. players, etc.
"""

from munerator.common.database import setup_eve_mongoengine

import logging
import datetime
from munerator.common.models import Votes, Gamemaps, PlayerVotes, Players, PlaylistItems, IntermediatePlaylist

log = logging.getLogger(__name__)


class VoteReduce(object):
    action = 'replace'
    last_run = datetime.datetime.min

    map_votes = """
    function(){
        var key = {
            player: this.player,
            gamemap: this.gamemap,
            gametype: this.gametype
        }
        var value = {
            score: this.vote,
            votes: [this._id]
        }
        emit(key, value);
    }
    """

    # summarize vote where each consecutive vote counts less
    reduce_votes = """
    function(key, values){
        var score = 0.0;
        var votes = [];
        values.forEach(function(value){
            score = score + (((value.score*2)-score) / 2);
            votes = votes.concat(value.votes);
        });

        return {
            score: score,
            votes: votes
        };
    }
    """

    def vote_reduce(self):
        """
        Reduce raw votes to votes per map/gametype/player
        combination and store in player_votes collection.

        Uses incremental map_reduce based on vote create time.
        """
        new_votes = Votes.objects(updated__gte=self.last_run)
        list(new_votes.map_reduce(self.map_votes, self.reduce_votes, {self.action: 'player_votes'}))
        self.last_run = datetime.datetime.now()
        # after first run set collection output mode to merge
        self.action = 'merge'


class Playlister(object):
    team_games = [3, 4, 5, 6, 7, 8, 9]

    map_maps = """
    function() {
        var key = {
            gamemap:this._id,
            gametype: null
        };
        var value = {
            score: 0.0,
            votes: [],
        };

        // emit for every map/playlist combination
        this.gametypes.forEach(function(gametype){
            key.gametype = gametype;
            emit(key, value);
        });
    }
    """

    map_player_votes = """
    function(){
        var key = {
            gamemap: this._id.gamemap,
            gametype: this._id.gametype
        }
        var value = {
            score: this.value.score,
            votes: this.value.votes
        }
        emit(key, value);
    }
    """

    sum_score = """
    function(key, values){
        var scores = [];
        var votes = [];

        values.forEach(function(value){
            scores.push(value.score);
            votes = votes.concat(value.votes);
        });

        return {
            score: Array.sum(scores),
            votes: votes
        };
    }
    """

    def generate_playlist(self):
        # online player ids and online player count
        log.debug('online players: %s' % Players.objects(online=True).scalar('name'))
        online_players = Players.objects(online=True).scalar('id')
        online_player_count = len(online_players)
        # normalized to value between 2-16
        normalized_count = min(16, max(2, online_player_count))
        log.debug('map search player count: %s' % normalized_count)

        # select maps suitable for online players
        suitable_maps = Gamemaps.objects(min_players__lte=normalized_count, max_players__gte=normalized_count)
        log.debug('suitable map count: %s' % suitable_maps.count())

        # if uneven number of players, don't do team games
        if online_player_count % 2:
            log.debug('uneven player count, filtering team games out')
            suitable_maps = suitable_maps.filter(__raw__={
                'gametypes': {
                    '$not': {
                        '$elemMatch': {'$in': self.team_games}
                    }
                }
            })
            log.debug('suitable map count: %s' % suitable_maps.count())

        # prime map results with suitable maps
        list(suitable_maps.map_reduce(
            self.map_maps, self.sum_score,
            {'replace': 'intermediate_playlist'}
        ))

        # add player votes scores onto suitable maps
        online_players_votes = PlayerVotes.objects(
            id__player__in=online_players,
            id__gamemap__in=suitable_maps.scalar('id')
        )
        list(online_players_votes.map_reduce(
            self.map_player_votes, self.sum_score,
            {'reduce': 'intermediate_playlist'}
        ))

        # update playlist with new items
        PlaylistItems.objects.delete()
        for item in IntermediatePlaylist.objects():
            PlaylistItems(
                gamemap=item.id.get('gamemap'),
                gametype=item.id.get('gametype'),
                score=item.value.get('score'),
                votes=item.value.get('votes')
            ).save()
        log.debug('playlist items count: %s', PlaylistItems.objects.count())

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    db = setup_eve_mongoengine()

    # reduce votes to per-player, per-map
    vr = VoteReduce()
    vr.vote_reduce()

    # get all valid maps
    pl = Playlister()
    pl.generate_playlist()
