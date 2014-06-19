import Ember from 'ember';

export default Ember.Route.extend({
    model: function() {
        this.poll();
        return this.store.find('game');
    },
    poll: function() {
        var _this = this;
        Ember.run.later( function() {
            _this.store.find('game'); 
            _this.poll();
        }, 5000 );
    }
});