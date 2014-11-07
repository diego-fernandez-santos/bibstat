(function(requirejs) {
    'use strict';

    requirejs.config({
        baseUrl: '/static/js/',
        urlArgs: "bust=" + (new Date()).getTime(),
        shim: {
            'bootstrap': ['jquery'],
            'bootstrap.datepicker': ['bootstrap'],
            'bootstrap.tokenfield': ['bootstrap'],
            'bootstrap.validator': ['bootstrap'],
            'bootstrap.validator.sv': ['bootstrap.validator'],
            'jquery.tablesorter': ['jquery'],
            'jquery.textrange': ['jquery'],
            'typeahead': ['jquery'],
        },
        paths: {

            /* Plugins */
            'bootstrap': ['plugins/bootstrap/3.2.0/js/bootstrap'],
            'bootstrap.datepicker': ['plugins/bootstrap-datepicker/1.3.0/bootstrap-datepicker'],
            'bootstrap.tokenfield': ['plugins/bootstrap-tokenfield/0.12.0/bootstrap-tokenfield'],
            'bootstrap.validator': ['plugins/bootstrap-validator/0.5.2/js/bootstrapValidator'],
            'bootstrap.validator.sv': ['plugins/bootstrap-validator/0.5.2/js/language/sv_SE'],
            'jquery': ['plugins/jquery/1.11.1/jquery'],
            'jquery.tablesorter': ['plugins/jquery/tablesorter/2.17.8/jquery.tablesorter.min'],
            'jquery.textrange': ['plugins/jquery/textrange/1.3.0/jquery-textrange'],
            'typeahead': ['plugins/typeaheadjs/0.10.5/typeahead.bundle'],
            'underscore': ['plugins/underscorejs/1.7.0/underscore-min'],

            /* App */
            'cell': ['app/cell/cell'],
            'cell.sum': ['app/cell/sum'],
            'dispatches': ['app/dispatches'],
            'survey': ['app/survey'],
            'surveys.dispatch': ['app/surveys/dispatch'],
            'login': ['app/login'],
            'libraries': ['app/libraries']
        },

        deps: ['app/main']
    });

    requirejs.onError = function(e) {
        console.log(e);
    };
})(requirejs);