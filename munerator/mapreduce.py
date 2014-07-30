"""
Reduce map into a playlist of most populair games to be played based current player votes, num. players, etc.
"""

from munerator.common.database import setup_eve_mongoengine

import logging
import datetime
from munerator.common.models import Games, Votes, Gamemaps, PlayerVotes, Players, PlaylistItems, IntermediatePlaylist


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
        self.action = 'reduce'


class Playlister(object):
    map_maps = """
    function() {
        // magic numbers
        var team_games = [3, 4, 5, 6, 7, 8, 9];
        var team_game_modifier = 0.1;
        var map_size_modifier = 0.1;
        var less_team_games = 0.5;
        var less_played_modifier = 1.5;
        var last_played_modifier = 0.5;
        var rerotate_hours = 24*7;
        var default_score = num_players / 2;

        var key = {
            gamemap:this._id,
            gametype: null
        };
        var modifier = 1.0;
        var modifiers = new Array;

        // get last played time modifier factor
        var now = new Date().getTime()/1000/60/60;
        if (this.last_played){
            var last_played = this.last_played.getTime()/1000/60/60;
            var last_played = Math.min(now - last_played, rerotate_hours) / rerotate_hours;
            last_played = Math.ceil(last_played * 100)/100
        } else {
            var last_played = 0.5;
        }
        if (last_played < 1){
            modifiers.push({name: 'recently played', factor: last_played});
            modifier = modifier * last_played;
        }

        // boost less played maps
        if (this.times_played <= played_median){
            modifiers.push({name: 'played lt. avg.', factor: less_played_modifier});
            modifier = modifier * less_played_modifier;
        }

        // don't favor maps with unsuitable size
        if (this.min_players > num_players || this.max_player < num_players){
            modifier = modifier * map_size_modifier;
            modifiers.push({name: 'not suitable size', factor: map_size_modifier})
        }

        // emit for every map/playlist combination
        this.gametypes.forEach(function(gametype){
            var value = {
                score: default_score,
                modifier: modifier,
                votes: [],
                modifiers: modifiers.slice(0)
            }

            // don't favor team games with uneven number of online players
            if (team_games.indexOf(gametype) >= 0 && num_players % 2){
                value.modifier = value.modifier * team_game_modifier;
                value.modifiers.push({name: 'no team games', factor: team_game_modifier})
            }

            // don't favor team games with low player count
            if (team_games.indexOf(gametype) >= 0 && num_players <= 2){
                value.modifier = value.modifier * less_team_games;
                value.modifiers.push({name: 'less team games', factor: less_team_games})
            }

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
            modifier: 1,
            votes: this.value.votes,
            modifiers: []
        }
        emit(key, value);
    }
    """

    # sum of scores and product of modifiers, concatting lists of metadata
    sum_score = """
    function(key, values){
        var scores = [];
        var votes = [];
        var modifier = 1;
        var modifiers = [];

        values.forEach(function(value){
            // calculate reduced values
            scores.push(value.score);
            modifier = Math.ceil(modifier * value.modifier * 100)/100;

            // metadata
            votes = votes.concat(value.votes);
            modifiers = modifiers.concat(value.modifiers);
        });

        return {
            score: Array.sum(scores),
            modifier: modifier,
            votes: votes,
            modifiers: modifiers
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
        suitable_maps = Gamemaps.objects()

        # don't replay recent maps
        recent_maps_ids = [x.id for x in Games.objects.order_by('-start').scalar('gamemap')[:3] if x]
        if recent_maps_ids:
            suitable_maps = suitable_maps.filter(id__nin=recent_maps_ids)
        log.debug('suitable map count: %s' % suitable_maps.count())

        # get median play count for maps
        played_median = suitable_maps.order_by('times_played')[len(suitable_maps) // 2].times_played
        log.debug('map play median: %s' % played_median)

        # prime map results with suitable maps
        list(suitable_maps.map_reduce(
            self.map_maps, self.sum_score,
            {'replace': 'intermediate_playlist'},
            scope={
                'num_players': normalized_count,
                'played_median': played_median
            }
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
                score=round(item.value.get('score') * item.value.get('modifier'), 3),
                votes=item.value.get('votes'),
                modifiers=item.value.get('modifiers')
            ).save()
        log.debug('playlist items count: %s', PlaylistItems.objects.count())

if __name__ == '__main__':
    from applib.textui import colprint

    logging.basicConfig(level=logging.DEBUG, format='%(message)s')

    db = setup_eve_mongoengine()

    # reduce votes to per-player, per-map
    vr = VoteReduce()
    vr.vote_reduce()

    # get all valid maps
    pl = Playlister()
    pl.generate_playlist()

    x = list()
    x.append(["Map", "Type", "Score", "Modifiers", "Votes"])

    playlistitems = list(PlaylistItems.objects.order_by('score'))
    for pli in playlistitems:
        x.append([
            pli.gamemap.name, str(pli.gametype), str(pli.score),
            ", ".join(['{name}:{factor}'.format(**m) for m in pli.modifiers]),
            ", ".join(['{0.player.name}:{0.vote}'.format(v) for v in pli.votes])
        ])
    x.append(["Map", "Type", "Score", "Modifiers", "Votes"])
    colprint(x)
