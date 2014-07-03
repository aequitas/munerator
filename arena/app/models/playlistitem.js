import DS from 'ember-data';

export default DS.Model.extend({
    gamemap: DS.belongsTo('gamemap', {async: true}),
    votes: DS.hasMany('vote', {async: true}),
    score: DS.attr('number')  
});
