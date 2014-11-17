# coding=utf-8
from sets import Set
from django import forms
from django.core.urlresolvers import reverse
from bibstat import settings
from libstat.models import Library, Survey, Variable, SurveyObservation
from libstat.survey_templates import survey_template


class LibrarySelection:

    def __init__(self, library):
        self.library = library

    def selectable_libraries(self):
        if not self.library.municipality_code:
            return []

        return Library.objects.filter(
            municipality_code=self.library.municipality_code,
            sigel__ne=self.library.sigel
        )

    def selected_sigels(self, sample_year):
        if not self.library.municipality_code:
            return Set()

        surveys = Survey.objects.filter(
            sample_year=sample_year,
            _library__municipality_code=self.library.municipality_code,
            _library__sigel__ne=self.library.sigel
        )

        selected_sigels = Set()
        for survey in surveys:
            for sigel in survey.selected_libraries:
                selected_sigels.add(sigel)

        return selected_sigels

    def has_conflicts(self, survey):
        for selected_sigel in self.selected_sigels(survey.sample_year):
            if selected_sigel in survey.selected_libraries:
                return True

        return False

    def get_conflicting_surveys(self, survey):
        if not self.library.municipality_code:
            return []

        other_surveys = Survey.objects.filter(
            sample_year=survey.sample_year,
            _library__municipality_code=self.library.municipality_code,
            _library__sigel__ne=self.library.sigel
        )

        return [
            other_survey for other_survey in other_surveys
            if any(s1 in other_survey.selected_libraries for s1 in survey.selected_libraries)
        ]


class SurveyForm(forms.Form):

    def _cell_to_input_field(self, cell, observation):
        attrs = {"class": "form-control",
                 "id": cell.variable_key,
                 "name": cell.variable_key}

        if cell.sum_of:
            attrs["data-sum-of"] = " ".join(map(lambda s: s, cell.sum_of))
            attrs["data-bv-notempty"] = ""
            attrs["placeholder"] = "Obligatorisk"

        if "required" in cell.types:
            attrs["data-bv-notempty"] = ""
            attrs["placeholder"] = "Obligatorisk"

        if "integer" in cell.types:
            attrs["data-bv-integer"] = ""
            attrs["data-bv-greaterthan"] = ""
            attrs["data-bv-greaterthan-value"] = "0"
            attrs["data-bv-greaterthan-inclusive"] = ""

        if "numeric" in cell.types:
            attrs["data-bv-numeric"] = ""
            attrs["data-bv-numeric-separator"] = "."
            attrs["data-bv-greaterthan"] = ""
            attrs["data-bv-greaterthan-value"] = "0"
            attrs["data-bv-greaterthan-inclusive"] = ""

        if "email" in cell.types:
            attrs["data-bv-emailaddress"] = ""
            attrs["data-bv-regexp"] = ""
            attrs["data-bv-regexp-regexp"] = ".+@.+\..+"
            attrs["data-bv-regexp-message"] = "Vänligen mata in en giltig emailadress"

        if "text" in cell.types:
            attrs["data-bv-stringlength"] = ""
            attrs["data-bv-stringlength-min"] = "0"

        if observation.disabled:
            attrs["disabled"] = ""

        if "comment" in cell.types:
            field = forms.CharField(required=False, widget=forms.Textarea(attrs=attrs))
        elif "integer" in cell.types:
            field = forms.IntegerField(required=False, widget=forms.TextInput(attrs=attrs))
        elif "email" in cell.types:
            field = forms.EmailField(required=False, widget=forms.TextInput(attrs=attrs))
        elif "numeric" in cell.types:
            field = forms.FloatField(required=False, widget=forms.TextInput(attrs=attrs))
        else:
            field = forms.CharField(required=False, widget=forms.TextInput(attrs=attrs))

        field.initial = u"Värdet är okänt" if observation.value_unknown else observation.value

        return field

    def _set_libraries(self, current_library, selected_libraries, authenticated):
        selection = LibrarySelection(current_library)
        selected_sigels = selection.selected_sigels(self.sample_year)

        def set_library(self, library, current_library=False):
            checkbox_id = str(library.sigel)

            attrs = {
                "value": checkbox_id,
                "class": "select-library"
            }

            row = {
                "name": library.name,
                "city": library.city,
                "address": library.address,
                "sigel": library.sigel,
                "checkbox_id": checkbox_id
            }

            if self.is_read_only:
                attrs["disabled"] = "true"

            if library.sigel in selected_sigels:
                attrs["disabled"] = "true"
                row["comment"] = u"Detta bibliotek rapporteras redan för i en annan enkät."
                if current_library or library.sigel in selected_libraries:
                    row["comment"] = u"Rapporteringen för detta bibliotek kolliderar med en annan enkät."
                    self.library_selection_conflict = True
                    del attrs["disabled"]

            if current_library:
                attrs["disabled"] = "true"
                if not authenticated or library.sigel in selected_libraries:
                    attrs["checked"] = "true"

                if not library.sigel in selected_sigels:
                    row["comment"] = u"Detta är det bibliotek som enkäten avser i första hand."
            elif library.sigel in selected_libraries:
                attrs["checked"] = "true"

            if authenticated:
                try:
                    del attrs["disabled"]
                except KeyError:
                    pass

            print(attrs)

            self.fields[checkbox_id] = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs=attrs))
            self.libraries.append(row)

        self.libraries = []
        set_library(self, current_library, current_library=True)
        for library in selection.selectable_libraries():
            set_library(self, library)

    def _status_label(self, key):
        return next((status[1] for status in Survey.STATUSES if status[0] == key))

    def __init__(self, *args, **kwargs):
        survey = kwargs.pop('survey', None)
        authenticated = kwargs.pop('authenticated', False)
        super(SurveyForm, self).__init__(*args, **kwargs)

        template = survey_template(survey.sample_year, survey)

        self.fields["disabled_inputs"] = forms.CharField(
            required=False, widget=forms.HiddenInput(attrs={"id": "disabled_inputs"}))
        self.fields["unknown_inputs"] = forms.CharField(
            required=False, widget=forms.HiddenInput(attrs={"id": "unknown_inputs"}))
        self.fields["selected_libraries"] = forms.CharField(
            required=False, widget=forms.HiddenInput(attrs={"id": "selected_libraries"}))
        self.fields["submit_action"] = forms.CharField(
            required=False, widget=forms.HiddenInput(attrs={"id": "submit_action"}))
        self.fields["read_only"] = forms.CharField(required=False, widget=forms.HiddenInput(attrs={"id": "read_only"}))
        self.fields["key"] = forms.CharField(required=False, widget=forms.HiddenInput(), initial=survey.pk)
        self.fields["selected_status"] = forms.CharField(
            required=False, widget=forms.HiddenInput(), initial=self._status_label(survey.status))
        self.fields["principal"] = forms.ChoiceField(required=False, choices=Survey.PRINCIPALS, initial=survey.principal)

        self.library_name = survey.library.name
        self.city = survey.library.city
        self.municipality_code = survey.library.municipality_code
        self.sample_year = survey.sample_year
        self.is_user_read_only = not survey.status in (u"not_viewed", u"initiated")
        self.is_read_only = not authenticated and self.is_user_read_only
        self.can_submit = not authenticated and survey.status in ("not_viewed", "initiated")
        self.password = survey.password
        self.status = self._status_label(survey.status)
        self.statuses = [status for status in Survey.STATUSES if not status[0] == "published"]
        self.is_published = survey.status == "published"
        self.sections = template.sections

        self.url = settings.API_BASE_URL + reverse('survey', args=(survey.pk,))
        self.url_with_password = "{}?p={}".format(self.url, self.password)

        self._set_libraries(survey.library, survey.selected_libraries, authenticated)
        if hasattr(self, 'library_selection_conflict') and self.library_selection_conflict:
            self.conflicting_surveys = LibrarySelection(survey.library).get_conflicting_surveys(survey)
            for conflicting_survey in self.conflicting_surveys:
                conflicting_survey.url = settings.API_BASE_URL + reverse('survey', args=(conflicting_survey.pk,))
            self.can_submit = False

        for section in template.sections:
            for group in section.groups:
                for row in group.rows:
                    for cell in row.cells:
                        variable_key = cell.variable_key
                        if len(Variable.objects.filter(key=variable_key)) == 0:
                            raise Exception("Can't find variable with key '{}'".format(variable_key))
                        observation = survey.get_observation(variable_key)

                        cell.disabled = observation.disabled
                        if not observation:
                            variable = Variable.objects.get(key=variable_key)
                            survey.observations.append(SurveyObservation(variable=variable,
                                                                         _source_key=variable.key))
                        self.fields[variable_key] = self._cell_to_input_field(cell, observation)

        if self.is_read_only:
            self.fields["read_only"].initial = "true"
            self.fields["principal"].widget.attrs["disabled"] = ""  # selects can't have the readonly attribute
            for key, input in self.fields.iteritems():
                input.widget.attrs["readonly"] = ""
