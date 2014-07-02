import Ember from 'ember';

export default Ember.Route.extend({
    model: function() {
        var items = Ember.A([]);
        var promise = this.store.find('gamemap', {'sort': '[("name",1)]'});

        promise.then(function(){
            items.pushObjects(promise.content.content);
        });
        return items;
    },
    actions: {
        getMore: function(){
            var newpage = this.controller.get('page') + 1;
            var more = this.store.find('gamemap', {page:newpage, 'sort': '[("name",1)]'});
            more.then(function(){
                this.get('controller').send('gotMore', more.content.content, newpage);
            }.bind(this));

        }
    }
});
