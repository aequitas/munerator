/* jshint node: true */

module.exports = function(environment) {
  var ENV = {
    baseURL: '/',
    locationType: 'auto',
    EmberENV: {
      FEATURES: {
        // Here you can enable experimental features on an ember canary build
        // e.g. 'with-controller': true
      }
    },

    APP: {
    }
  };

  if (environment === 'development') {
    // LOG_MODULE_RESOLVER is needed for pre-1.6.0
    ENV.LOG_MODULE_RESOLVER = false;

    ENV.APP.LOG_RESOLVER = false;
    ENV.APP.LOG_ACTIVE_GENERATION = false;
    ENV.APP.LOG_MODULE_RESOLVER = false;
    // ENV.APP.LOG_TRANSITIONS = false;
    // ENV.APP.LOG_TRANSITIONS_INTERNAL = false;
    ENV.APP.LOG_VIEW_LOOKUPS = false;

    ENV.api_endpoint = 'http://quake.brensen.com:8081'; // live url
    // ENV.api_endpoint = 'http://localhost:8081'; // live url
  }

  if (environment === 'production') {
    ENV.locationType = 'hash';
    ENV.api_endpoint = '';
  }

  return ENV;
};
