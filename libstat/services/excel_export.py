# -*- coding: utf-8 -*-
from time import time
from openpyxl import Workbook
from data.principals import principal_for_library_type
from libstat.models import Survey, OpenData


def public_excel_export(year):
    workbook = Workbook(encoding="utf-8")
    worksheet = workbook.active

    variable_keys = list(OpenData.objects.filter(is_active=True, sample_year=year).distinct("variable_key"))
    sigels = list(OpenData.objects.filter(is_active=True, sample_year=year).distinct("sigel"))

    libraries = {}
    for sigel in sigels:
        libraries[sigel] = dict.fromkeys(variable_keys)

    for open_data in OpenData.objects.filter(is_active=True, sample_year=year).only("library_name", "variable_key",
                                                                                    "sigel", "value"):
        libraries[open_data.sigel][open_data.variable_key] = open_data.value

    header = ["Bibliotek", "Sigel", "Bibliotekstyp", "Kommunkod", "Stad", "Adress"]
    variable_index = {}
    for index, key in enumerate(variable_keys):
        variable_index[key] = index + 6
        header.append(key)
    worksheet.append(header)

    for sigel in libraries:
        library = Survey.objects.get(library__sigel=sigel).library
        row = [""] * len(header)
        row[0] = library.name
        row[1] = sigel
        row[2] = library.library_type
        row[3] = library.municipality_code
        row[4] = library.city
        row[5] = library.address

        for key in variable_keys:
            row[variable_index[key]] = libraries[sigel][key]
        worksheet.append(row)

    return workbook


def surveys_to_excel_workbook(survey_ids):
    surveys = Survey.objects.filter(id__in=survey_ids).order_by('library__name')

    headers = [
        "Bibliotek",
        "Sigel",
        "Bibliotekstyp",
        "Status",
        "Email",
        "Kommunkod",
        "Stad",
        "Adress",
        "Huvudman",
        "Kan publiceras?"
    ]
    headers += [unicode(observation.variable.key) for observation in surveys[0].observations]

    workbook = Workbook(encoding="utf-8")
    worksheet = workbook.active
    worksheet.append(headers)

    for survey in surveys:
        row = [
            survey.library.name,
            survey.library.sigel,
            survey.library.library_type,
            Survey.status_label(survey.status),
            survey.library.email,
            survey.library.municipality_code,
            survey.library.city,
            survey.library.address,
            principal_for_library_type[survey.library.library_type]
            if survey.library.library_type in principal_for_library_type else None,
            "Ja" if survey.can_publish() else "Nej: " + survey.reasons_for_not_able_to_publish()
        ]
        for observation in survey.observations:
            row.append(observation.value)
        worksheet.append(row)

    return workbook