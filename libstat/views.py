# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.http import HttpResponse, HttpResponseRedirect
from django.http import Http404
from django.conf import settings

from libstat.models import Variable, SurveyResponse
from libstat.forms import *
from django.contrib.auth.decorators import permission_required

from libstat.apis import *

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

@permission_required('is_superuser', login_url='login')
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
    try: 
        v = Variable.objects.get(pk=variable_id)
    except Exception:
        raise Http404

    if request.method == "POST":
        # TODO: work in progress...
        form = VariableForm(request.POST)
        if form.is_valid():
#             try:
#                 form.save(v)
#                 return HttpResponse(u"Variable updated")
#             except ValidationError as ve:
#                 for error_message in ve.messages:
#                     form.add_form_error(error_message)
            return HttpResponse(u"Variable updated")
        else:
            print form.errors
    else:    
        form = VariableForm(instance=v)
        
    context = {'form': form }
    return render(request, 'libstat/modals/edit_variable.html', context)

@permission_required('is_superuser', login_url='login')
def survey_responses(request):
    s_responses = []
    
    # TODO: Cache sample_years
    sample_years = SurveyResponse.objects.distinct("sample_year")
    sample_years.sort()
    sample_years.reverse()
    
    action = request.GET.get("action", "")
    target_group = request.GET.get("target_group", "")
    sample_year = request.GET.get("sample_year", "")
    
    if action == "list":
        s_responses = SurveyResponse.objects.by_year_or_group(sample_year=sample_year, target_group=target_group).order_by("library")
  
    context = { 
         'sample_years': sample_years,
         'survey_responses': s_responses,
         'target_group': target_group,
         'sample_year': sample_year,
         'bibdb_library_base_url': u"{}/library".format(settings.BIBDB_BASE_URL)
    }
    return render(request, 'libstat/survey_responses.html', context)

@permission_required('is_superuser', login_url='login')
def publish_survey_responses(request):
    if request.method == "POST":
        target_group = request.POST.get("target_group", "")
        sample_year = request.POST.get("sample_year", "")
        
        print(u"Publish requested for {} {}".format(target_group, sample_year))
        
        s_responses = SurveyResponse.objects.by_year_or_group(sample_year=sample_year, target_group=target_group)
        for sr in s_responses:
            try:
                sr.publish()
            except Exception as e:
                print u"Error when publishing survey response {} {} {}: {}".format(sr.sample_year, sr.target_groups, sr.library_name, e)
        
    # TODO: There has to be a better way to do this...
    return HttpResponseRedirect(u"{}{}".format(reverse("survey_responses"), u"?action=list&target_group={}&sample_year={}".format(target_group, sample_year)))
    
