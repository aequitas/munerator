/* global require, module */

var EmberApp = require('ember-cli/lib/broccoli/ember-app');

var app = new EmberApp();

app.import('vendor/momentjs/moment.js');
app.import('vendor/bootstrap-sass-official/vendor/assets/javascripts/bootstrap.js');
app.import('vendor/bootstrap-sass-official/vendor/assets/javascripts/bootstrap/collapse.js');

// Put the bootstrap fonts in the place that the bootstrap css expects to find them.
var pickFiles = require('broccoli-static-compiler');
var bootstrapFonts = pickFiles('vendor/bootstrap-sass-official/vendor/assets/fonts/bootstrap', {
    srcDir: '/',
    destDir: '/assets/bootstrap'
});

// Merge the bootstrapFonts with the ember app tree
var mergeTrees = require('broccoli-merge-trees');
module.exports = mergeTrees([app.toTree(),bootstrapFonts]);