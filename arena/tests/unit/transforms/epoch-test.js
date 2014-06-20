import { test, moduleFor } from 'ember-qunit';

moduleFor('transform:epoch', 'EpochTransform', {
  // Specify the other units that are required for this test.
  // needs: ['serializer:foo']
});

test('converts python epoch to date', function() {
  var transform = this.subject();

  var epoch = '1403268702.480765';

  var date = moment.unix(epoch).toDate();

  deepEqual(transform.deserialize(epoch), date, 'Epoch should deserialize to Date');
});
