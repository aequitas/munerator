var Player = DS.Model.extend({
    name: DS.attr('string'),
    team: DS.attr('string'),
});

Player.reopenClass({
    FIXTURES: [
        {
            id: 1,
            name: '-[aequitas]-',
            team: 'red'
        },
        {
            id: 2,
            name: 'n00b',
            team: 'blue'
        }
    ]
});

export default Player;