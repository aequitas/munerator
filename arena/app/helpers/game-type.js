import Ember from 'ember';

var gametypes = ['Deathmatch','Tournament','Single Player','Team Deathmatch (TDM)','Capture The Flag (CTF)',
'One Flag Capture','Overload','Harvester','Elimination','CTF Elimination','Last Man Standing',
'Double Domination','Domination'];

export default Ember.Handlebars.makeBoundHelper(function(value) {
  return gametypes[value];
});


