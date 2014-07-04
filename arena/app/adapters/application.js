import DS from "ember-data";
import Ember from "ember";

// export default DS.FixtureAdapter.extend({
//     queryFixtures: function(fixtures){
//         return fixtures;
//     }
// });

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
        hash.data.ts = Math.round(new Date().getTime()/10000);
        return this._super(url, type, hash);
    },
    findMany: function(store, type, ids) {
        var data = { where: '_id=="' + ids.join('" or _id=="') + '"'};
        return this.ajax(this.buildURL(type.typeKey), 'GET', { data: data });
    },
});
