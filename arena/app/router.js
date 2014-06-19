import Ember from 'ember';

var Router = Ember.Router.extend({
  location: ArenaENV.locationType
});

Router.map(function() {
  this.resource('games', { path: '/games' });
  this.resource('players', { path: '/players' });
  this.resource('player', { path: '/player/:player_id' }, function() {
    this.route('edit');
  });
});

export default Router;
