import DS from "ember-data";
import Ember from "ember";

var Player = DS.Model.extend({
    name: DS.attr('string'),
    team: DS.attr('string'),
    online: DS.attr('boolean'),
    score: DS.attr('number'),
    // games: DS.hasMany('game'),

    poll: function() {
        var _this = this;
        Ember.run.later( function() {
            _this.reload(); 
            _this.poll();
        }, 5000 );
    }.observes('didLoad').on('init')
});

Player.reopenClass({
    FIXTURES: [
        {
            id: 0,
            name: '-[aequitas]-',
            team: 'red',
            online: true,
            score: 42
        },
        {
            id: 1,
            name: 'n00b',
            team: 'blue',
            online: true,
            score: 0
        }
    ]
});

export default Player;