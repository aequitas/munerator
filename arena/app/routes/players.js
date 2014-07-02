import Ember from 'ember';
import PollingRouteMixin from './polling';

export default Ember.Route.extend(PollingRouteMixin, {
    model: function() {
        return this.store.find('player', {'sort': '[("updated",-1)]'});
    }
});