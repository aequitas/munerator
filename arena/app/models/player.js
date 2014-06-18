import DS from "ember-data";
import Ember from "ember";

var Player = DS.Model.extend({
    name: DS.attr('string'),
    team: DS.attr('string'),
    online: DS.attr('boolean'),

    poll: function() {
        var _this = this;
        Ember.run.later( function() {
            _this.reload(); 
            _this.poll();
        }, 500 );
    }.observes('didLoad')
});

Player.reopenClass({
    FIXTURES: [
        {
            id: '9982DEAC44F27E0622FCF0FC6C540F45',
            name: '-[aequitas]-',
            team: 'red',
            online: true
        },
        {
            id: '9CD101D150811D227AB7EF2C65082083',
            name: 'n00b',
            team: 'blue',
            online: true
        }
    ]
});

export default Player;