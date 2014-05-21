# -*- coding: UTF-8 -*-
from mongoengine import *
from pip._vendor.pkg_resources import require

# Create your models here.

PUBLIC_LIBRARY = "PublicLibrary"
RESEARCH_LIBRARY = "ResearchLibrary"
HOSPITAL_LIBRARY = "HospitalLibrary"
SCHOOL_LIBRARY = "SchoolLibrary"
 
SURVEY_TARGET_GROUPS = [PUBLIC_LIBRARY, RESEARCH_LIBRARY, HOSPITAL_LIBRARY, SCHOOL_LIBRARY]

OBSERVATION_TYPE_INT = "Integer",
OBSERVATION_TYPE_STR = "String",
OBSERVATION_TYPE_SEK = "Currency_SEK"

OBSERVATION_TYPES = [OBSERVATION_TYPE_INT, OBSERVATION_TYPE_STR, OBSERVATION_TYPE_SEK]

"""
Variables
[
    {
        "id": "fpweijf+9u3+r9u3493+49u",
        "key": "noOfEmployees_Librarian_M",
        "aliases": ["folk18"],
        "description": "Antal anställda bibliotekarier som är män",
        "is_public": True
    },
    {
        "id": "sd0f98s0d9f80s9d8f0d9f9s",
        "key": "noOfEmployees_Librarian_F",
        "aliases": ["folk17"],
        "description": "Antal anställda bibliotekarier som är kvinnor",
        "is_public": True
    },
    {
        "id": "sd0f9s8df098sd0f9sydf86d5",
        "key": "comment_OtherLendingPlaces",
        "aliases": ["folk15"]
        "description": "Textkommentar övriga utlåningsställen",
        "is_public": False
    },
]
"""
class Variable(Document):
    key = StringField(max_length=100, required=True, unique=True)
    aliases = ListField(StringField(max_length=100), required=True)
    description = StringField(max_length=300, required=True)
    comment = StringField(max_length=200)
    
    is_public = BooleanField(required=True, default=True)
    target_groups = ListField(StringField(max_length=20), required=True)
#     observation_type = StringField(max_length=20, required=True, default="Integer")

    meta = {
        'collection': 'libstat_variables'
    }

    def __unicode__(self):
        return self.key

"""
    Question
    {
        "id": "093ur093u0983029823098",
        "parent": null, 
        "question": "Hur stort bokbestånd hade folkbiblioteket totalt den 31 december 2012?",
        "variable": null
    },
    {
        "id": "f79d87f9sd6fs7f6s7d6f9s7df",
        "parent": "093ur093u0983029823098", 
        "question": "Hur stort bokbestånd hade folkbiblioteket totalt den 31 december 2012?",
        "variable": "sd6f6s8fa9df9ad7f9a7df9"
    },
    -------- OR PERHAPS:
    {
        "id": "093ur093u0983029823098",
        "question": "Hur stort bokbestånd hade folkbiblioteket totalt den 31 december 2012?",
        "variable": null, 
        "question_parts": [
            {
                "part": "Skönlitteratur för vuxna",
                "variable": "sd6f6s8fa9df9ad7f9a7df9"
            },
            {
                "part": "Skönlitteratur för barn",
                "variable": "2309482039r8203982"
            }
        ]
    }
"""
class Question(Document):
    parent = ReferenceField('Question')
    question = StringField(required=True)
     
    # Not required if this is a parent question
    variable = ReferenceField(Variable)
     
    meta = {
        'collection': 'libstat_questions'
    }
 
class Survey(Document):
    target_group = StringField(max_length=20, required=True, choices=SURVEY_TARGET_GROUPS)
    sampleYear = IntField(required=True)
    questions = ListField(ReferenceField(Question), required=True)
     
    meta = {
        'collection': 'libstat_surveys'
    }
     
    def __unicode__(self):
        return u"{} {}".format(self.target_group, self.sampleYear)

"""
SurveyResponse
{
    "id": "07sdf5df08sfg9s8g09sf9",
    "library": "Kls1",
    "refArea": "Karlstad",
    "sampleYear": 2013,
    "observations": [
        <SurveyObservation> {
            "variable": "fpweijf+9u3+r9u3493+49u",
            "value": 6,
            "_variable_key": "folk18",
            "_is_public": True
        },
        <SurveyObservation> {
            "variable": "sd0f98s0d9f80s9d8f0d9f9s",
            "value": 23
            "_variable_key": "folk17",
            "_is_public": True
        },
        <SurveyObservation> {
            "variable": "sd0f9s8df098sd0f9sydf86d5",
            "value": "Boksnurror i köpcentret"
            "_variable_key": "folk15",
            "_is_public": False
        }
    ]
}
"""
class SurveyObservation(EmbeddedDocument):
    variable = ReferenceField(Variable, required=True)
    value = DynamicField(required=True)

    # Keeping the original key reference from spreadsheet for traceability
    _source_key = StringField(max_length=100)
    
    # Public API Optimization and traceability (was this field public at the time of the survey?)
    _is_public = BooleanField(required=True, default=True)

    def __unicode__(self):
        return u"{0}: {1}".format(self.variable, self.value)

class SurveyResponse(Document):
    library = StringField(max_length=50, required=True)
    sampleYear = IntField(required=True)

    observations = ListField(EmbeddedDocumentField(SurveyObservation))

    meta = {
        'collection': 'libstat_survey_response'
    }

    def __unicode__(self):
        return u"{0}: {1}".format(self.respondent, self.observations)
