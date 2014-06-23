import { test, moduleFor } from 'ember-qunit';

import quakeName from 'arena/helpers/quake-name';

test('quake name should be converted to colored html', function() {
    equal(quakeName.helper('colors^11^22^33^44^55^66^77^0w00t'), '<span class="quake-color-0">colors</span><span class="quake-color-1">1</span><span class="quake-color-2">2</span><span class="quake-color-3">3</span><span class="quake-color-4">4</span><span class="quake-color-5">5</span><span class="quake-color-6">6</span><span class="quake-color-7">7</span><span class="quake-color-0">w00t</span>');
});
