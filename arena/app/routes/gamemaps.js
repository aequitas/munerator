import Ember from 'ember';
import InfiniteScroll from 'arena/infinite_scroll';

export default Ember.Route.extend(InfiniteScroll.RouteMixin, {
    setupController: function(controller) {
        this.fetchPage(1).then(function(items){
            controller.set('content', items.get('content'));
            controller.set('total', items.get('meta.total'));
        });
    },
    fetchPage: function(page){
        return this.store.find('gamemap', {'sort': '[("name",1)]', 'page': page});
    }
});
