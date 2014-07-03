import Ember from 'ember';
import PollingRouteMixin from './polling';

export default Ember.Route.extend(PollingRouteMixin, {
    controllerName: 'game',
    setupController:function(controller, context){
        controller.set('content', context.content.get('firstObject'));
    },
    model: function(){
        return this.store.find('game', {'sort': '[("updated",-1)]'});
    }
});
