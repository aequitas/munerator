import Ember from 'ember';

export default Ember.Route.extend({
    model: function() {
        return this.store.find('vote', {'max_results': 30, 'sort': '[("_created",1)]'});
    },
});
