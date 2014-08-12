# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, resolve_url
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from django.conf import settings

from libstat.models import Variable, SurveyResponse
from libstat.forms import *
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from django.utils.http import is_safe_url
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache

from libstat.apis import *

import logging
logger = logging.getLogger(__name__)

def index(request):
    context = {
        "nav_start_css": "active",
        "nav_open_data_css": ""
    }
    return render(request, 'libstat/index.html', context)

def open_data(request):
    context = {
        "nav_start_css": "",
        "nav_open_data_css": "active",
        "api_base_url": settings.API_BASE_URL
    }
    return render(request, 'libstat/open_data.html', context)
    
@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request):
    """
        Login modal view
    """
    redirect_to = _get_listview_from_modalview(request.REQUEST.get("next", ""))
    
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():

            # Ensure the user-originating redirection url is safe.
            if not is_safe_url(url=redirect_to, host=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

            # Okay, security check complete. Log the user in.
            auth_login(request, form.get_user())

            context = {
                'next': redirect_to
            }
            return HttpResponse(json.dumps(context), content_type="application/json")
        else:
            context = {
                'errors': form.errors,
                'next': redirect_to
            }
            return HttpResponse(json.dumps(context), content_type="application/json")
            
    else:
        form = AuthenticationForm(request)

    context = {
        'form': form,
        'next': redirect_to,
    }
    return render(request, 'libstat/modals/login.html', context)

def _get_listview_from_modalview(relative_url=""):
    if reverse("variables") in relative_url:
        return reverse("variables")
    return relative_url
    

@permission_required('is_superuser', login_url='index')
def variables(request):
    target_group = request.GET.get("target_group", "")
    if target_group:
        variables = Variable.objects.filter(target_groups__in=[target_group])
    else:
        variables = Variable.objects.order_by("key")
    context = { 
        'variables': variables,
        'target_group': target_group
    }
    return render(request, 'libstat/variables.html', context)

@permission_required('is_superuser', login_url='login')
def edit_variable(request, variable_id):
    """
        Edit variable modal view
    """
    try: 
        v = Variable.objects.get(pk=variable_id)
    except Exception:
        raise Http404

    if request.method == "POST":
        errors = {}
        form = VariableForm(request.POST, instance=v)
        if form.is_valid():
            try:
                v = form.save();
                return HttpResponse(v.to_json(), content_type="application/json")
            except Exception as e:
                logger.warning(u"Error updating Variable {}: {}".format(variable_id, e))
                errors['__all__'] = [u"Kan inte uppdatera term {}".format(v.key)]
                
        else:
            errors = form.errors
        context = {
            'errors': errors
        }
        return HttpResponse(json.dumps(context), content_type="application/json")
    else:    
        form = VariableForm(instance=v)
        
    context = {'form': form }
    return render(request, 'libstat/modals/edit_variable.html', context)

@permission_required('is_superuser', login_url='index')
def survey_responses(request):
    s_responses = []
    
    # TODO: Cache sample_years
    sample_years = SurveyResponse.objects.distinct("sample_year")
    sample_years.sort()
    sample_years.reverse()
    
    action = request.GET.get("action", "")
    target_group = request.GET.get("target_group", "")
    sample_year = request.GET.get("sample_year", "")
    unpublished_only = request.GET.get("unpublished_only", False);
    if "True" == unpublished_only:
        unpublished_only = True
    else:
        unpublished_only = False
    
    if action == "list":
        # TODO: Pagination
        if unpublished_only:
            s_responses = SurveyResponse.objects.unpublished_by_year_or_group(sample_year=sample_year, target_group=target_group).order_by("library")
        else:
            s_responses = SurveyResponse.objects.by_year_or_group(sample_year=sample_year, target_group=target_group).order_by("library")
  
    context = { 
         'sample_years': sample_years,
         'survey_responses': s_responses,
         'target_group': target_group,
         'sample_year': sample_year,
         'unpublished_only': unpublished_only,
         'bibdb_library_base_url': u"{}/library".format(settings.BIBDB_BASE_URL)
    }
    return render(request, 'libstat/survey_responses.html', context)

@permission_required('is_superuser', login_url='index')
def publish_survey_responses(request):
    MAX_PUBLISH_LIMIT = 500
        
    if request.method == "POST":
        target_group = request.POST.get("target_group", "")
        sample_year = request.POST.get("sample_year", "")
        survey_response_ids = request.POST.getlist("survey-response-ids", [])
        
        logger.info(u"Publish requested for {} survey response ids".format(len(survey_response_ids)))
        
        if len(survey_response_ids) > MAX_PUBLISH_LIMIT:
            survey_response_ids = survey_response_ids[:MAX_PUBLISH_LIMIT]
            logger.warning(u"That seems like an awful lot of objects to handle in one transaction, limiting to first {}".format(MAX_PUBLISH_LIMIT))
            
        
        if len(survey_response_ids) > 0:
            s_responses = SurveyResponse.objects.filter(id__in=survey_response_ids)
            for sr in s_responses:
                try:
                    sr.publish()
                except Exception as e:
                    logger.error(u"Error when publishing survey response {}:".format(sr.id))
                    print e
        
    # TODO: There has to be a better way to do this...
    return HttpResponseRedirect(u"{}{}".format(reverse("survey_responses"), u"?action=list&target_group={}&sample_year={}".format(target_group, sample_year)))

@permission_required('is_superuser', login_url='index')
def edit_survey_response(request, survey_response_id):
    try:
        survey_response = SurveyResponse.objects.get(pk=survey_response_id)
    except:
        raise Http404
    
    form = CustomSurveyResponseForm(instance=survey_response)
#     observation_forms = []
#     for i in range(len(survey_response.observations)):
#         observation_forms.append(SurveyObservationForm(parent_document=survey_response, position=i))
         
    context = {
        'form': form, 
#         'observation_forms': observation_forms
    }
    return render(request, 'libstat/edit_survey_response.html', context)
    