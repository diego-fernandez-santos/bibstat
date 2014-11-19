# -*- coding: UTF-8 -*-
import requests

from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import permission_required

from libstat.models import Library, LibrarySelection, Survey, SurveyObservation, Variable
from libstat.forms.create_surveys import CreateSurveysForm
from libstat.views.surveys import _surveys_redirect
from libstat.survey_templates import survey_template


def _create_surveys(library_ids, sample_year):
    def survey_exists(sigel, sample_year):
        return Survey.objects.filter(_library__sigel=sigel,sample_year=sample_year).first() is not None

    created = 0
    for library_id in library_ids:
        library = Library.objects.get(pk=library_id)
        if survey_exists(library.sigel, sample_year):
            continue

        template = survey_template(sample_year)
        survey = Survey(
            library=library,
            sample_year=sample_year,
            observations=[])
        for section in template.sections:
            for group in section.groups:
                for row in group.rows:
                    for cell in row.cells:
                        variable_key = cell.variable_key
                        if len(Variable.objects.filter(key=variable_key)) == 0:
                            raise Exception("Can't find variable with key '{}'".format(variable_key))
                        survey.observations.append(
                            SurveyObservation(
                                variable=Variable.objects.get(key=variable_key)))
        survey.save()
        created += 1

    return created


@permission_required('is_superuser', login_url='index')
def libraries(request):
    if request.method == "POST":
        form = CreateSurveysForm(request.POST)
        if form.is_valid():
            sample_year = int(form.cleaned_data.pop("sample_year"))
            library_ids = []
            for field in form.cleaned_data:
                if form.cleaned_data[field]:
                    library_ids.append(field)
        if "create_surveys_btn" in form.data:
            created = _create_surveys(library_ids, sample_year)

            message = u""
            if created > 0:
                message = u"Skapade {} stycken nya enkäter för de markerade biblioteken.".format(created)
            if created < len(library_ids):
                if len(message) > 0: message += u"\n"
                message += u"För {} stycken av biblioteken fanns redan enkäter skapade.".format(len(library_ids) - created);
            request.session["message"] = message

            return _surveys_redirect(request)
        elif "save_selection_btn" in form.data:
            lib_selection, _ = LibrarySelection.objects.get_or_create(name="lib_selection")
            lib_selection.sigels = []
            for lib_id in library_ids:
                lib_selection.sigels.append(Library.objects.get(pk=lib_id).sigel)
            lib_selection.save()

    return render(request, 'libstat/libraries.html', {"form": CreateSurveysForm()})


def _dict_to_library(dict):
    if not dict["country_code"] == "se":
        return None

    library, _ = Library.objects.get_or_create(sigel=dict["sigel"])
    library.sigel = dict.get("sigel") if dict.get("sigel") else None
    library.name = dict.get("name") if dict.get("name") else None
    library.municipality_code = dict.get("municipality_code") if dict.get("municipality_code") else None
    library.library_type = dict.get("library_type") if dict.get("library_type") else None
    location = next((a for a in dict["address"] if a["address_type"] == "gen"), None)
    library.address = location["street"] if location and location["street"] else None
    library.city = location["city"] if location and location["city"] else None
    library.email = next((c["email"] for c in dict["contact"]
                          if "email" in c and c["contact_type"] == "statans"), None)

    return library


def _update_libraries():
    # bibdb api paginated by 200 and had ca. 2800 responses when this was written
    for start_index in range(0, 6000, 200):
        response = requests.get(
            url="http://bibdb.libris.kb.se/api/lib?dump=true&start=%d" % start_index,
            headers={"APIKEY_AUTH_HEADER": "bibstataccess"})

        for lib_data in response.json()["libraries"]:
            library = _dict_to_library(lib_data)
            if library:
                library.save()


@permission_required('is_superuser', login_url='index')
def remove_libraries(request):
    Library.objects.all().delete()
    return redirect(reverse('libraries'))


@permission_required('is_superuser', login_url='index')
def import_libraries(request):
    _update_libraries()
    return redirect(reverse('libraries'))
