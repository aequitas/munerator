import Ember from 'ember';
import PollingRouteMixin from './polling';

export default Ember.Route.extend(PollingRouteMixin, {
    controllerName: 'playlistitems',
    model: function(){
        return this.store.find('playlistitem', {'sort': '[("score",1)]'});
    }
});