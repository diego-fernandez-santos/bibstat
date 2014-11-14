# -*- coding: utf-8 -*-
import logging

from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound
from django.contrib.auth.decorators import permission_required

from libstat.models import Survey
from libstat.forms.survey import SurveyForm


logger = logging.getLogger(__name__)


def _save_survey_response_from_form(response, form):
    if form.is_valid():
        disabled_inputs = form.cleaned_data.pop("disabled_inputs").split(" ")
        unknown_inputs = form.cleaned_data.pop("unknown_inputs").split(" ")
        response.principal = form.cleaned_data.pop("principal")
        submit_action = form.cleaned_data.pop("submit_action", None)
        print(submit_action)
        if submit_action == "submit" and response.status in ("not_viewed", "initiated"):
            response.status = "submitted"

        for field in form.cleaned_data:
            observation = response.get_observation(field)
            if observation:
                observation.value = form.cleaned_data[field]
                observation.disabled = (field in disabled_inputs)
                observation.value_unknown = (field in unknown_inputs)
            else:
                response.__dict__["_data"][field] = form.cleaned_data[field]

        response.selected_libraries = form.cleaned_data["selected_libraries"].split(" ")
        response.save()
    else:
        raise Exception(form.errors)


def survey(request, survey_id):

    def has_password():
        return request.method == "GET" and "p" in request.GET or request.method == "POST"

    def get_password():
        return request.GET["p"] if request.method == "GET" else request.POST.get("password", None)

    def can_view_survey(survey):
        return request.user.is_authenticated() or request.session.get("password") == survey.id

    try:
        survey = Survey.objects.get(pk=survey_id)
    except Survey.DoesNotExist:
        return HttpResponseNotFound()

    context = {
        'survey_id': survey_id,
    }

    if not request.user.is_superuser:
        context["hide_navbar"] = True

    if can_view_survey(survey):
        if request.method == "POST":
            form = SurveyForm(request.POST, survey=survey)
            _save_survey_response_from_form(survey, form)

        if not request.user.is_authenticated() and survey.status == "not_viewed":
            survey.status = "initiated"
            survey.save()

        context["form"] = SurveyForm(survey=survey, authenticated=request.user.is_authenticated())
        return render(request, 'libstat/survey.html', context)

    if has_password():
        if get_password() == survey.password:
            request.session["password"] = survey.id
            request.session.set_expiry(0)
            return redirect(reverse("survey", args=(survey_id,)))
        else:
            context["wrong_password"] = True

    return render(request, 'libstat/survey/password.html', context)


@permission_required('is_superuser', login_url='index')
def survey_status(request, survey_id):
    if request.method == "POST":
        status = request.POST[u'selected_status']
        survey = Survey.objects.get(pk=survey_id)
        survey.status = status
        survey.save()

    return redirect(reverse('survey', args=(survey_id,)))