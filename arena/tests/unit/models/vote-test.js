import { test, moduleForModel } from 'ember-qunit';

moduleForModel('vote', 'Vote', {
  // Specify the other units that are required for this test.
  needs: ['model:player', 'model:game']
});

test('it exists', function() {
  var model = this.subject();
  // var store = this.store();
  ok(model);
});
