import Ember from 'ember';

var InfiniteScroll = {
    PAGE:     1,  // default start page
    PER_PAGE: 25 // default per page
};

InfiniteScroll.ControllerMixin = Ember.Mixin.create({
    loadingMore: false,
    page: InfiniteScroll.PAGE,
    perPage: InfiniteScroll.PER_PAGE,
    actions: {
        getMore: function(){
            if (this.get('loadingMore')) {
                return;
            }

            this.set('loadingMore', true);
            this.get('target').send('getMore');
        },

        gotMore: function(items, nextPage){
            this.set('loadingMore', false);
            this.pushObjects(items);
            this.set('page', nextPage);
        }
    }
});

InfiniteScroll.RouteMixin = Ember.Mixin.create({
    actions: {
        getMore: function() {
            throw new Error("Must override Route action `getMore`.");
        },
        fetchPage: function() {
            throw new Error("Must override Route action `getMore`.");
        }
    }
});

export default InfiniteScroll;