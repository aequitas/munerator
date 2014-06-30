import Ember from 'ember';

export default Ember.Route.extend({
    controllerName: 'game',

    model: function(){
        return this.store.find('game', {where: '{"current":true}'}).then(function (obj) {
            return obj.get('firstObject');
        });
    }
});
