import DS from "ember-data";
import Ember from "ember";

export default DS.RESTAdapter.extend({
    host: ArenaENV.api_endpoint,
    namespace: 'api/1',
    ajax: function(url, type, hash) {
        if (Ember.isEmpty(hash)) {
            hash = {};
        }
        if (Ember.isEmpty(hash.data)) {
            hash.data = {};
        }
        hash.data.ts = new Date().getTime();
        return this._super(url, type, hash);
    }
});
