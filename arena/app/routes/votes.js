import Ember from 'ember';
import PollingRouteMixin from './polling';

export default Ember.Route.extend(PollingRouteMixin, {
    model: function() {
        return this.store.find('vote', {'max_results': 15, 'sort': '[("updated",-1)]'});
    },
});
