import DS from "ember-data";

var Game = DS.Model.extend({
    mapname: DS.attr('string'),
    current: DS.attr('boolean'),
    start: DS.attr('epoch'),
    stop: DS.attr('epoch'),
    players: DS.hasMany('player', {async: true})
});

Game.reopenClass({
    FIXTURES: [
        {
            id: 1,
            map: 'awesomemap',
            current: true,
            players: [
                0,
                1
            ],
            start: moment().toDate(),
            stop: null
        },
        {
            id: 2,
            map: 'lastmap',
            current: false,
            start: moment().subtract('hour').toDate(),
            stop: moment().toDate()
        }
    ]
});

export default Game;