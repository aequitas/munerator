db = connect("munerator");

// online players and online player count
var online_players = [];
db.players.find({online:true}).forEach(function(player){
    online_players.push(player._id);
});
var num_players = online_players.length;

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

// only maps fitting for player count and not recently played
map_query = {
    min_players: { $lte: num_players },
    max_players: { $gte: num_players },
    $or: [ 
        { last_played: { $lte: new Date(ISODate().getTime() - 1000 * 60 * 60)} },
        { last_played: { $exists: false } }
    ]
};

function votes_map(){
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

// summarize map score 
function sum_score(key, values){
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

// only select votes for current online players
var vote_query = {
    player: {$in: online_players}
};

// prime reduce results with maps
// db.gamemaps.mapReduce(maps_map, sum_score, { out: { replace:'reduced' }, query: map_query });
// // merge vote scores onto maps
db.votes.mapReduce(votes_map, sum_score, { out: { merge: 'reduced' }, query: vote_query });

// // replace playlist with new items
db.playlist_items.remove({});
db.reduced.find({'value.score':{$gte:0}}).forEach(function(item){
    db.playlist_items.insert(item.value);
});

// // // show it
print(db.playlist_items.find().count());
// db.playlist_items.find().forEach(function(value){
//     printjson(value);
// });

