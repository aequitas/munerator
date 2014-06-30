import Ember from 'ember';
import PollingRouteMixin from './polling';

export default Ember.Route.extend(PollingRouteMixin, {
    controllerName: 'game',

    model: function(){
        return this.store.find('game', {where: '{"current":true}'}).then(function (obj) {
            return obj.get('firstObject');
        });
    }
});
