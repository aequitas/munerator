import DS from 'ember-data';

export default DS.Transform.extend({
  deserialize: function(serialized) {
    var data = [];

    for (var item in serialized){
        data.push({name: item, value: serialized[item]});
    }

    return data;
  },

  serialize: function(deserialized) {
    return deserialized;
  }
});
