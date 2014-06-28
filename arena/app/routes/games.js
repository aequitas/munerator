import Ember from 'ember';

export default Ember.Route.extend({
    model: function() {
        return this.store.find('game', {'max_results': 15, 'sort': '[("updated",-1)]'});
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
            _this.refresh();
            _this.poll();
        }, 10000 );
        this.set('poll_inst', poll_inst);
    }
});