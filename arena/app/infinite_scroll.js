import Ember from 'ember';

var InfiniteScroll = {
    PAGE:     1,  // default start page
    PER_PAGE: 25 // default per page
};

InfiniteScroll.ControllerMixin = Ember.Mixin.create({
    loadingMore: false,
    page: InfiniteScroll.PAGE,
    perPage: InfiniteScroll.PER_PAGE,

    hasMore: function(){
        return this.get('total') > this.get('content.length');
    }.property('@each'),

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
        getMore: function(){
            var newpage = this.controller.get('page') + 1;
            var more = this.model(newpage);
            more.then(function(){
                this.get('controller').send('gotMore', more.content.content, newpage);
            }.bind(this));

        }
    }
});

export default InfiniteScroll;
