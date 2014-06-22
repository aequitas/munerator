import Ember from 'ember';

export default Ember.Handlebars.makeBoundHelper(function(value) {
    var escaped = Handlebars.Utils.escapeExpression(value);

    escaped = escaped.replace(/\^([0-9])/,'<span class="quake-color-$1">');
    escaped = escaped.replace(/\^([0-9])/g,'</span><span class="quake-color-$1">');

    if (escaped.indexOf('<span class') !== -1){
        escaped = escaped + '</span>';
    }

    return new Ember.Handlebars.SafeString(escaped);
});