import DS from 'ember-data';

export default DS.Model.extend({
    gamemap: DS.belongsTo('gamemap', {async: true}),
    gametype: DS.attr('number'),
    votes: DS.hasMany('vote', {async: true}),
    score: DS.attr('number')  
});
