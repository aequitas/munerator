import Ember from 'ember';

var helper = function(value) {
    var escaped = Ember.Handlebars.Utils.escapeExpression(value);

    escaped = escaped.replace(/\^([0-9])/g,'</span><span class="quake-color-$1">');
    escaped = '<span class="quake-color-0">' + escaped + '</span>';

    return new Ember.Handlebars.SafeString(escaped);
};

var quakeName = Ember.Handlebars.makeBoundHelper(helper);
quakeName.helper = helper;

export default quakeName;