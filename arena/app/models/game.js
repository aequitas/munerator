import DS from "ember-data";

var Game = DS.Model.extend({
    mapname: DS.attr('string'),
    gamemap: DS.belongsTo('gamemap', {async: true}),
    gametype: DS.attr('number'),
    current: DS.attr('boolean'),
    start: DS.attr('epoch'),
    stop: DS.attr('epoch'),
    players: DS.hasMany('player', {async: true}),
    votes: DS.hasMany('vote', {async: true}),
    options: DS.attr('dict'),
    _updated: DS.attr('date'),
    _created: DS.attr('date')
});

Game.reopenClass({
    FIXTURES: [
        {
            id: 1,
            gamemap: 1,
            gametype: 0,
            current: true,
            players: [
                '2394808AFSDFAFS',
                '23948ASDF08AFSDFAFS'
            ],
            start: moment().toDate(),
            stop: null
        },
        {
            id: 2,
            gamemap: 2,
            gametype: 1,
            current: false,
            start: moment().subtract('hour').toDate(),
            stop: moment().toDate()
        }
    ]
});

export default Game;