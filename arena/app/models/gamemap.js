var GameMap = DS.Model.extend({
    name: DS.attr('string'),
    current: DS.attr('boolean'),
});

GameMap.reopenClass({
    FIXTURES: [
        {
            id: 1,
            name: 'awesomemap',
            current: true
        },
        {
            id: 2,
            name: 'lastmap',
            current: false
        }
    ]
});

export default GameMap;