import DS from "ember-data";

// export default DS.FixtureAdapter.extend({});

export default DS.RESTAdapter.extend({
    host: ArenaENV.api_endpoint,
    namespace: 'api/1'
});
