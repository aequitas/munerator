import Ember from 'ember';
import InfiniteScroll from 'arena/infinite_scroll';

export default Ember.ArrayController.extend(InfiniteScroll.ControllerMixin, {
    sortProperties: ['online', 'team', 'score', '_updated'],
    sortAscending: false
});
