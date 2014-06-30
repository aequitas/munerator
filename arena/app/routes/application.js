import Ember from 'ember';

export default Ember.Route.extend({
    actions: {
        // prevent loading screen when refreshing current page
        loading: function(transition) {
            if (transition.urlMethod === 'replace'){
                return false;
            }
            return true;
        }
    }
});
