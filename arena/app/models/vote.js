import DS from 'ember-data';

export default DS.Model.extend({
    vote: DS.attr('number'),
    player: DS.belongsTo('player', {async: true}),
    game: DS.belongsTo('game', {async: true}),
    _updated: DS.attr('date')
});
