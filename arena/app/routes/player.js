import Ember from 'ember';

export default Ember.Route.extend({
    setupController: function(controller, model){
        this._super(controller, model);
        this.poll(model);
    },
    deactivate: function(){
        Ember.run.cancel(this.get('poll_inst'));
    },
    poll: function(model) {
        var _this = this;
        var poll_inst = Ember.run.later( function() {
            model.reload();
            _this.poll(model);
        }, 5000 );
        this.set('poll_inst', poll_inst);
    }
});
