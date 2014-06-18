import Ember from 'ember';

export default Ember.Route.extend({
    model: function() {
        this.poll();
        return this.store.find('player');
    },
    poll: function() {
        var _this = this;
        Ember.run.later( function() {
            _this.store.find('player'); 
            _this.poll();
        }, 1000 );
    }.observes('didLoad')

});