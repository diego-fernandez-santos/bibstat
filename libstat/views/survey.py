# -*- coding: utf-8 -*-
import logging
import time
import json

from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound, HttpResponseForbidden, HttpResponse
from django.contrib.auth.decorators import permission_required
from django.forms.util import ErrorList

from bibstat import settings

from libstat.models import Survey, Variable, SurveyObservation, Library
from libstat.forms.survey import SurveyForm
from libstat.survey_templates import survey_template

logger = logging.getLogger(__name__)


def example_survey(request):
    sample_year = 2014

    context = {
        "hide_navbar": True,
        "hide_bottom_bar": True,
        "hide_admin_panel": True,
        "form": SurveyForm(survey=Survey(
            sample_year=sample_year,
            library=Library(
                name=u"Exempelbiblioteket",
                sigel=u"exempel_sigel",
                email=u"exempel@email.com",
                city=u"Exempelstaden",
                municipality_code=180,
                address=u"Exempelgatan 14B",
                library_type=u"folkbib"
            ),
            observations=[SurveyObservation(variable=Variable.objects.get(key=cell.variable_key))
                          for cell in survey_template(sample_year).cells])),
    }
    return render(request, 'libstat/survey.html', context)


def _validate_sums(survey, form, submit_action):
    not_valid_sum_fields = []

    def isnumber(obj):
        return isinstance(obj, (int, long, float, complex))

    def isempty(obj):
        if not obj:
            return True
        if isnumber(obj) and obj == 0:
            return True
        if not isnumber(obj) and obj == "0" or obj == "0,0" or obj == "":
            return True
        return False

    for section in form.sections:
        for group in section.groups:
            for row in group.rows:
                for cell in row.cells:
                    if cell.sum_of:
                        total = 0
                        # no subfield values are entered -> sum doesn't need to be validated
                        if all([isempty(survey.get_observation(f).value) for f in cell.sum_of]):
                            continue
                        try:
                            for field in cell.sum_of:
                                observation = survey.get_observation(field)
                                if observation and observation.value:
                                    observation_value = observation.value
                                else:
                                    continue
                                if isnumber(observation_value):
                                    total += observation_value
                                else:
                                    total += float(observation_value)
                            if survey.get_observation(cell.variable_key) and survey.get_observation(cell.variable_key).value:
                                sum_value = survey.get_observation(cell.variable_key).value
                            elif cell.required and submit_action == 'submit': # empty cells only generate error if required and action is 'submit'
                                not_valid_sum_fields.append(cell.variable_key)
                                continue
                            elif submit_action == 'save':
                                continue
                            if not isnumber(sum_value):
                                sum_value = float(sum_value)
                            if not sum_value == total:
                                not_valid_sum_fields.append(cell.variable_key)
                        except Exception as e:
                            logger.debug("Excepting and added field to not valid sums. Exception: %s" % e)
                            not_valid_sum_fields.append(cell.variable_key)
    return not_valid_sum_fields

# Validation of sums
def _has_valid_sums(survey, form, submit_action):
    not_valid_sum_list = _validate_sums(survey, form, submit_action)
    if len(not_valid_sum_list) > 0:
        for variable_key in not_valid_sum_list:
            form._errors[variable_key] = ErrorList([u"Vänligen kontrollera att summan stämmer överens med delvärdena, alternativt fyll bara i en totalsumma."]) # form._errors not used in response at the mo as form post is done w ajax and does not return whole form
        return False
    return True


def _save_survey_response_from_form(survey, form):
    error_list = []

    if form.is_valid():
        disabled_inputs = form.cleaned_data.pop("disabled_inputs").split(" ")
        unknown_inputs = form.cleaned_data.pop("unknown_inputs").split(" ")
        submit_action = form.cleaned_data.pop("submit_action", None)
        altered_fields = form.cleaned_data.pop("altered_fields", None).split(" ")

        for field in form.cleaned_data:
            observation = survey.get_observation(field)
            if observation:
                if field in altered_fields:
                    observation.value = form.cleaned_data[field]
                    observation.disabled = (field in disabled_inputs)
                    observation.value_unknown = (field in unknown_inputs)
            else:
                survey.__dict__["_data"][field] = form.cleaned_data[field]

        survey.selected_libraries = filter(None, form.cleaned_data["selected_libraries"].split(" "))

        if _has_valid_sums(survey, form, submit_action):

            if submit_action == "submit" and survey.status in ("not_viewed", "initiated"):
                if not survey.has_conflicts():
                    survey.status = "submitted"

            survey.save()

    for field_name in form.cleaned_data:
        field_errors = form[field_name].errors
        if len(field_errors) > 0:
            error_dict = {}
            error_dict["fieldName"] = field_name
            error_dict["errorMessage"] = form[field_name].errors.as_text()
            error_list.append(error_dict)

    return {"errors": error_list}


def survey(request, survey_id):
    def has_password():
        return request.method == "GET" and "p" in request.GET or request.method == "POST"

    def get_password():
        return request.GET["p"] if request.method == "GET" else request.POST.get("password", None)

    def can_view_survey(survey):
        return request.user.is_authenticated() or request.session.get("password") == survey.id

    survey = Survey.objects.filter(pk=survey_id)
    if len(survey) != 1:
        return HttpResponseNotFound()

    survey = survey[0]

    if not survey.is_active and not request.user.is_authenticated():
        return HttpResponseForbidden()

    context = {
        'survey_id': survey_id,
    }

    if not request.user.is_superuser:
        context["hide_navbar"] = True

    if not request.user.is_authenticated() and settings.BLOCK_SURVEY:
        return render(request, "libstat/survey_blocked.html")

    if can_view_survey(survey):

        if not request.user.is_authenticated() and survey.status == "not_viewed":
            survey.status = "initiated"
            survey.save()

        if request.method == "POST":
            form = SurveyForm(request.POST, survey=survey)
            errors = _save_survey_response_from_form(survey, form) # Errors returned as separate json
            logger.debug("ERRORS: ")
            logger.debug(json.dumps(errors))
            return HttpResponse(json.dumps(errors), content_type="application/json")
        else:
            context["form"] = SurveyForm(survey=survey, authenticated=request.user.is_authenticated())
            return render(request, 'libstat/survey.html', context)

    if has_password():
        if get_password() == survey.password:
            request.session["password"] = survey.id
            return redirect(reverse("survey", args=(survey_id,)))
        else:
            context["wrong_password"] = True

    return render(request, 'libstat/survey/password.html', context)


@permission_required('is_superuser', login_url='index')
def survey_status(request, survey_id):
    if request.method == "POST":
        survey = Survey.objects.get(pk=survey_id)
        survey.status = request.POST[u'selected_status']
        survey.save()

    return redirect(reverse('survey', args=(survey_id,)))


@permission_required('is_superuser', login_url='index')
def survey_notes(request, survey_id):
    if request.method == "POST":
        survey = Survey.objects.get(pk=survey_id)
        survey.notes = request.POST[u'notes']
        survey.save()

    return redirect(reverse('survey', args=(survey_id,)))
