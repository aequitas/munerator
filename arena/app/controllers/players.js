import Ember from 'ember';

export default Ember.ArrayController.extend({
    sortProperties: ['online', 'team', 'score', '_updated'],
    sortAscending: false,
    hasMore: function(){
        return this.get('content.meta.total') > this.get('content.length');
    }.property('@each'),
});
