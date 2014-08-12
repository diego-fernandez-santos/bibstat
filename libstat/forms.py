# -*- coding: UTF-8 -*-
from mongodbforms import DocumentForm, EmbeddedDocumentForm
from libstat.fieldgenerator import FormFieldGenerator
from django import forms
from libstat.models import Variable, variable_types, SurveyResponse, SurveyObservation, SURVEY_TARGET_GROUPS, SurveyResponseMetadata

#TODO: Define a LoginForm class with extra css-class 'form-control' ?

class VariableForm(DocumentForm):
    question = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    question_part = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    category = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    sub_category = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    # Since this is a checkbox, a value will only be returned in form if the checkbox is checked. Hence the required=False.
    is_public = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'value':'1'}))
    
    description = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '2'}))
    comment = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '2'}))
    
    class Meta:
        model = Variable
        fields = ["question", "question_part", "category", "sub_category", "type", "is_public", "target_groups", "description", "comment"]
        formfield_generator = FormFieldGenerator(widget_overrides={'stringfield_choices': forms.RadioSelect})

class SurveyResponseForm(DocumentForm):
    library_name = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'size': '50', 'maxlength': '100'}))
    
    class Meta:
        model = SurveyResponse
        fields = ["library_name", "target_group", "sample_year", "published_at"]
        
class SurveyObservationForm(EmbeddedDocumentForm):
    value = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    class Meta:
        document = SurveyObservation
        embedded_field_name = 'observations'
        fields = ["value"]
        
class CustomSurveyResponseForm(forms.Form):
    """
        Custom form for creating/editing a SurveyResponse with all embedded documents.
    """
    sample_year = forms.CharField(required=True, max_length=4, widget=forms.HiddenInput) #TODO: Remove or make hidden
    target_group = forms.CharField(required=True, widget=forms.HiddenInput) # TODO: Remove or make hidden
    
    library_name = forms.CharField(required=True, max_length=100, widget=forms.TextInput(attrs={'class': 'form-control width-auto', 'size': '58'}))
    municipality_name = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={'class': 'form-control width-auto', 'size': '58'}))
    municipality_code = forms.CharField(required=False, max_length=6, widget=forms.TextInput(attrs={'class': 'form-control width-auto', 'size': '6'}))
    
    respondent_name = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={'class': 'form-control width-auto', 'size': '58'}))
    respondent_email = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={'class': 'form-control width-auto', 'size': '58'}))
    respondent_phone = forms.CharField(required=False, max_length=20, widget=forms.TextInput(attrs={'class': 'form-control width-auto', 'size': '20'}))
    
    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        
        sample_year = kwargs.pop('sample_year', None)
        target_group = kwargs.pop('target_group', None)
        library_name = kwargs.pop('library_name', None)
        
        super(CustomSurveyResponseForm, self).__init__(*args, **kwargs)
        
        self.fields['target_group'].choices = [target_group for target_group in SURVEY_TARGET_GROUPS]
        
        if self.instance:
            self.fields['sample_year'].initial = self.instance.sample_year
            self.fields['target_group'].initial = self.instance.target_group
            self.fields['library_name'].initial = self.instance.library_name
            self.fields['municipality_name'].initial = self.instance.metadata.municipality_name if self.instance.metadata else None
            self.fields['municipality_code'].initial = self.instance.metadata.municipality_code if self.instance.metadata else None
            self.fields['respondent_name'].initial = self.instance.metadata.respondent_name if self.instance.metadata else None
            self.fields['respondent_email'].initial = self.instance.metadata.respondent_email if self.instance.metadata else None
            self.fields['respondent_phone'].initial = self.instance.metadata.respondent_phone if self.instance.metadata else None
        else:
            self.fields['sample_year'] = sample_year
            self.fields['target_group'] = target_group
            self.fields['library_name'] = library_name
            
            
    def save(self, commit=True):
      surveyResponse = self.instance if self.instance else SurveyResponse()
      surveyResponse.library_name = self.cleaned_data['library_name']
      surveyResponse.sample_year = self.cleaned_data['sample_year']
      surveyResponse.target_group = self.cleaned_data['target_group']
      
      surveyResponse.metadata = self.instance.metadata if self.instance.metadata and (self.cleaned_data['municipality_name'] or self.cleaned_data['municipality_code']) else SurveyResponseMetadata()
      surveyResponse.metadata.municipality_name = self.cleaned_data['municipality_name']
      surveyResponse.metadata.municipality_code = self.cleaned_data['municipality_code']
      surveyResponse.metadata.respondent_name = self.cleaned_data['respondent_name']
      surveyResponse.metadata.respondent_email = self.cleaned_data['respondent_email']
      surveyResponse.metadata.respondent_phone = self.cleaned_data['respondent_phone']
      
      if commit:
          surveyResponse.save()

      return surveyResponse

    