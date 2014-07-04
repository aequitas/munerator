import DS from 'ember-data';

var Gamemap = DS.Model.extend({
    name: DS.attr('string'),
    levelshot: DS.attr('string'),
    images: DS.attr('raw'),
    gametypes: DS.attr('raw'),
    min_players: DS.attr('number'),
    max_players: DS.attr('number'),
    times_played: DS.attr('number'),
    last_played: DS.attr('date'),
    _updated: DS.attr('date'),
    _created: DS.attr('date')
});

Gamemap.reopenClass({
    FIXTURES: [
        {
            id: 1,
            name: 'awesomemap',
            levelshot: 'http://ws.q3df.org/images/levelshots/128x96/bubctf1.jpg',
            images: [
                'http://ws.q3df.org/images/levelshots/512x384/bubctf1.jpg',
                'http://ws.q3df.org/images/topviews/512x384/bubctf1.jpg'
            ],
            gametypes: [4,5]
        },
        {
            id: 2,
            name: 'lastmap',
            levelshot: 'http://ws.q3df.org/images/levelshots/128x96/',
            gametypes: [0]
        }
    ]
});

export default Gamemap;