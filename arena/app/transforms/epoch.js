import DS from 'ember-data';

export default DS.Transform.extend({
  deserialize: function(serialized) {
    if (serialized){
        return moment.unix(serialized).toDate();
    } else {
        return null;
    }
  },

  serialize: function(deserialized) {
    return moment(deserialized).format('X.SS');
  }
});
