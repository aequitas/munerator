import Ember from 'ember';
import PollingRouteMixin from './polling';
import InfiniteScroll from 'arena/infinite_scroll';

export default Ember.Route.extend(PollingRouteMixin, InfiniteScroll.RouteMixin, {
    controllerName: 'playlistitems',

    setupController: function(controller) {
        this.fetchPage(1).then(function(items){
            controller.set('content', items.get('content'));
            controller.set('total', items.get('meta.total'));
        });
    },
    fetchPage: function(page){
        return this.store.find('playlistitem', {'sort': '[("score",-1)]', 'page': page});
    }
});
