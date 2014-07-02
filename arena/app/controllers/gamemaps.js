import Ember from 'ember';
import InfiniteScroll from 'arena/infinite_scroll';

export default Ember.ArrayController.extend(InfiniteScroll.ControllerMixin, {
    sortProperties: ['name'],
    sortAscending: true,
    hasMore: function(){
        return this.get('total') > this.get('perPage') * this.get('page');
    }.property('page', 'total'),
    total: function(){
        return this.store.metadataFor('gamemap').total;
    }.property('@each')

});
