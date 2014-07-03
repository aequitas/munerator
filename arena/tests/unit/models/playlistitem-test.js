import { test, moduleForModel } from 'ember-qunit';

moduleForModel('playlistitem', 'Playlistitem', {
  // Specify the other units that are required for this test.
  needs: ['model:vote', 'model:gamemap']
});

test('it exists', function() {
  var model = this.subject();
  // var store = this.store();
  ok(model);
});
