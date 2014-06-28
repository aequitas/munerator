import DS from 'ember-data';

export default DS.RESTSerializer.extend({
    extractArray: function(store, type, payload) {
        payload[type.typeKey] = payload._items;
        delete payload._items;
        delete payload._links;

        return this._super(store, type, payload);
    },
    extractSingle: function(store, type, payload, id) {
        var _payload = {};
        _payload[type.typeKey] = payload;

        return this._super(store, type, _payload, id);
    },
    extractMeta: function(store, type, payload) {
        payload.meta = payload._meta;
        delete payload._meta;
        return this._super(store, type, payload);
    },
    primaryKey: '_id'
});
