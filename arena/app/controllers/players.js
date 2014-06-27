import Ember from 'ember';

export default Ember.ArrayController.extend({
    sortProperties: ['online', 'team', 'score'],
    sortAscending: false
});
