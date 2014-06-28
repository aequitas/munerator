import Ember from 'ember';

export default Ember.ArrayController.extend({
    sortProperties: ['_updated'],
    sortAscending: false
});
