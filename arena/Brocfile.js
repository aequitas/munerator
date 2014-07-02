/* global require, module */

var EmberApp = require('ember-cli/lib/broccoli/ember-app');

var app = new EmberApp();

app.import('vendor/momentjs/moment.js');
app.import('vendor/bootstrap-sass-official/vendor/assets/javascripts/bootstrap.js');
app.import('vendor/bootstrap-sass-official/vendor/assets/javascripts/bootstrap/collapse.js');

// Standard Bootstrap javascript
['collapse.js'].forEach(function (path) {
  var fullPath = 'vendor/bootstrap-sass-official/vendor/assets/javascripts/bootstrap/' + path;
  app.import(fullPath);
});

// Bootstrap for ember
// Careful adding additional modules here - some require full handlebars.js, and by default ember-cli only includes runtime in production
['bs-core.min.js', 'bs-modal.min.js', 'bs-label.min.js', 'bs-button.min.js', 'bs-basic.min.js', 'bs-popover.min.js', 'bs-progressbar.min.js'].forEach(function (path) {
  var fullPath = 'vendor/ember-addons.bs_for_ember/dist/js/' + path;
  app.import(fullPath);
});

// Put the bootstrap fonts in the place that the bootstrap css expects to find them.
var pickFiles = require('broccoli-static-compiler');
var bootstrapFonts = pickFiles('vendor/bootstrap-sass-official/vendor/assets/fonts/bootstrap', {
    srcDir: '/',
    destDir: '/assets/bootstrap'
});

// Merge the bootstrapFonts with the ember app tree
var mergeTrees = require('broccoli-merge-trees');
module.exports = mergeTrees([app.toTree(),bootstrapFonts]);