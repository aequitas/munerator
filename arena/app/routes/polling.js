import Ember from 'ember';

export default Ember.Mixin.create({
    poll_interval: 10000,
    allowPoll: true,
    activate: function(){
        this.poll();
    },
    deactivate: function(){
        Ember.run.cancel(this.get('poll_inst'));
    },
    poll: function() {
        var poll_inst = Ember.run.later( function() {
            if (this.get('allowPoll')){
                this.controller.set('isPolling', true);
                this.refresh().then(function(){
                    this.controller.set('isPolling', false);
                    this.poll();
                }.bind(this));
            }
        }.bind(this), this.get('poll_interval'));
        this.set('poll_inst', poll_inst);
    }
});