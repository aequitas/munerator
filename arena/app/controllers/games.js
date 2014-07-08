import Ember from 'ember';
import InfiniteScroll from 'arena/infinite_scroll';

export default Ember.ArrayController.extend(InfiniteScroll.ControllerMixin, {
    sortProperties: ['_updated'],
    sortAscending: false
});
