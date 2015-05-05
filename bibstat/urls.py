from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse_lazy
from django.views.generic import RedirectView, TemplateView
from django.contrib.auth.views import logout

from django.contrib import admin
import libstat
from libstat.apis.open_data import data_api, observation_api, export_api
from libstat.apis.terms import term_api, terms_api

from libstat.views.auth import login
from libstat.views.administration import administration, create_new_collection
from libstat.views.articles import article, articles, articles_delete
from libstat.views.dispatches import dispatches, dispatches_delete, dispatches_send
from libstat.views.index import index
from libstat.views.reports import reports, report
from libstat.views.surveys import (surveys,
                                   surveys_statuses,
                                   surveys_export,
                                   surveys_activate,
                                   surveys_inactivate,
                                   surveys_overview,
                                   import_and_create,
                                   remove_empty,
                                   match_libraries,
                                   surveys_update_library)
from libstat.views.survey import (survey,
                                  survey_status,
                                  survey_notes,
                                  survey_print_view,
                                  example_survey)
from libstat.views.variables import (variables,
                                     edit_variable,
                                     create_variable, replaceable_variables)

admin.autodiscover()

urlpatterns = patterns('',

    url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain'), name="robots"),
    url(r'^humans\.txt$', TemplateView.as_view(template_name='humans.txt', content_type='text/plain; charset=utf-8'), name="humans"),

    # APIs
    url(r'^data$', data_api, name="data_api"),
    url(r'^data/(?P<observation_id>\w+)$', observation_api, name="observation_api"),
    url(r'^def/terms$', terms_api, name="terms_api"),
    url(r'^def/terms/(?P<term_key>\w+)$', term_api, name="term_api"),
    url(r'^export$', export_api, name='export_api'),

    # Auth
    url(r'^login$', login, name='login'),
    url(r'^logout$', logout, {'next_page': 'admin'}, name='logout'),

    # Index
    url(r'^$', index, name='index'),
    url(r'^admin$', libstat.views.index.admin, name='admin'),

    # Articles
    url(r'^article/(?P<article_id>\w+)$', article, name='article'),
    url(r'^article$', article, name='article'),
    url(r'^articles$', articles, name='articles'),
    url(r'^articles/delete/(?P<article_id>\w+)$', articles_delete, name='articles_delete'),

    # Reports
    url(r'^reports$', reports, name='reports'),
    url(r'^report$', report, name='report'),

    # Administration
    url(r'^administration/create_new_collection$', create_new_collection, name='create_new_collection'),
    url(r'^administration$', administration, name='administration'),

    # Survey
    url(r'^surveys$', surveys, name='surveys'),
    url(r'^surveys/example$', example_survey, name='example_survey'),
    url(r'^surveys/activate$', surveys_activate, name='surveys_activate'),
    url(r'^surveys/inactivate$', surveys_inactivate, name='surveys_inactivate'),
    url(r'^surveys/export$', surveys_export, name='surveys_export'),
    url(r'^surveys/import_and_create$', import_and_create, name='surveys_import_and_create'),
    url(r'^surveys/remove_empty$', remove_empty, name='surveys_remove_empty'),
    url(r'^surveys/match_libraries$', match_libraries, name='surveys_match_libraries'),
    url(r'^surveys/status$', surveys_statuses, name='surveys_statuses'),
    url(r'^surveys/overview/(?P<sample_year>\w+)$', surveys_overview, name='surveys_overview'),
    url(r'^surveys/status/(?P<survey_id>\w+)$', survey_status, name='survey_status'),
    url(r'^surveys/notes/(?P<survey_id>\w+)$', survey_notes, name='survey_notes'),
    url(r'^surveys/print/(?P<survey_id>\w+)$', survey_print_view, name='survey_print_view'),
    url(r'^surveys/update_library$', surveys_update_library, name='surveys_update_library'),
    url(r'^surveys/(?P<survey_id>\w+)$', survey, name='survey'),

    # Dispatch
    url(r'^dispatches$', dispatches, name='dispatches'),
    url(r'^dispatches/delete$', dispatches_delete, name='dispatches_delete'),
    url(r'^dispatches/send', dispatches_send, name='dispatches_send'),

    # Variables
    url(r'^variables$', variables, name='variables'),
    url(r'^variables/new$', create_variable, name='create_variable'),
    url(r'^variables/replaceable$', replaceable_variables, name='replaceable_variables'),
    url(r'^variables/(?P<variable_id>\w+)$', edit_variable, name='edit_variable'),

    # Other
    url(r'^.well-known/void$', RedirectView.as_view(url=reverse_lazy('open_data'), permanent=False)),
    url(r'^jsreverse/$', 'django_js_reverse.views.urls_js', name='js_reverse')
)
