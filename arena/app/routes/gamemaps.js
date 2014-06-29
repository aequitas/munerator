import Ember from 'ember';

export default Ember.Route.extend({
    model: function() {
        return this.store.find('gamemap', {'max_results': 30, 'sort': '[("updated",-1)]'});
    }
});
