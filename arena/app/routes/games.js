import Ember from 'ember';

export default Ember.Route.extend({
    model: function() {
        return this.store.find('game');
    },
    activate: function(){
        this.poll();
    },
    deactivate: function(){
        Ember.run.cancel(this.get('poll_inst'));
    },
    poll: function() {
        var _this = this;
        var poll_inst = Ember.run.later( function() {
            _this.store.find('game');
            _this.poll();
        }, 10000 );
        this.set('poll_inst', poll_inst);
    }
});