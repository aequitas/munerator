import Ember from 'ember';

var Router = Ember.Router.extend({
  location: ArenaENV.locationType
});

Router.map(function() {
    this.resource('players', { path: '/' });
    this.resource('maps', { path: '/maps' });
});

export default Router;
