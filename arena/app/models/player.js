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
            id: '2394808AFSDFAFS',
            name: '-[aequitas]-',
            team: 'red',
            online: true,
            score: 42
        },
        {
            id: '23948ASDF08AFSDFAFS',
            name: 'n00b',
            team: 'red',
            online: true,
            score: 0
        },
        {
            id: '23948SFADFJKLASDF08AFSDFAFS',
            name: 'colors^11^22^33^44^55^66^77^0w00t',
            team: '',
            online: false,
            score: 0
        }
    ]
});

export default Player;
