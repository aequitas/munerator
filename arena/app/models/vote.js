import DS from 'ember-data';

var Vote = DS.Model.extend({
    vote: DS.attr('number'),
    player: DS.belongsTo('player', {async: true}),
    game: DS.belongsTo('game', {async: true}),
    _updated: DS.attr('date'),
    _created: DS.attr('date')
});

Vote.reopenClass({
    FIXTURES: [
        {
            id: 1,
            game: 1,
            player: '2394808AFSDFAFS',
            vote: 1
        }
    ]
});

export default Vote;