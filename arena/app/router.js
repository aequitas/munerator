import Ember from 'ember';

var Router = Ember.Router.extend({
  location: ArenaENV.locationType
});

Router.map(function() {
  this.resource('games');
  this.resource('players');
  this.resource('player', { path: '/players/:player_id' });
  this.resource('votes');
  this.resource('game', { path: '/games/:game_id' });
});

export default Router;