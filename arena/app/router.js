import Ember from 'ember';

var Router = Ember.Router.extend({
  location: ArenaENV.locationType
});

Router.map(function() {
  this.resource('games');
  this.resource('game', { path: '/games/:game_id' });

  this.resource('players');
  this.resource('player', { path: '/players/:player_id' });
  
  this.resource('gamemaps');
  this.resource('gamemap', { path: '/gamemaps/:gamemap_id' });

  this.resource('votes');

  this.route('playlist');
});

export default Router;