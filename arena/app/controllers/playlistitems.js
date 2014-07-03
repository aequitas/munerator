import Ember from 'ember';

export default Ember.ArrayController.extend({
    sortProperties: ['score'],
    sortAscending: false
});
