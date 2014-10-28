# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect

from bibstat import settings
from libstat.models import Dispatch, Survey


def _rendered_template(template, survey):
    survey_url = settings.API_BASE_URL + reverse('survey', args=(survey.id,))

    rendered = template.replace(u"{bibliotek}", survey.library.name)
    rendered = rendered.replace(u"{lösenord}", survey.password)
    rendered = rendered.replace(u"{enkätadress}", survey_url)

    return rendered


@permission_required('is_superuser', login_url='login')
def dispatches(request):
    if request.method == "POST":
        survey_ids = request.POST.getlist("survey-response-ids", [])
        surveys = Survey.objects.filter(id__in=survey_ids)

        for survey in surveys:
            Dispatch(
                message=_rendered_template(request.POST["message"], survey),
                title=_rendered_template(request.POST["title"], survey),
                description=request.POST["description"],
                survey=survey
            ).save()

        return redirect(reverse("dispatches"))

    if request.method == "GET":
        dispatches = [
            {
                "description": dispatch.description,
                "title": dispatch.title,
                "message": dispatch.message.replace("\n", "<br>"),
                "library_name": dispatch.survey.library.name,
                "library_city": dispatch.survey.library.city,
                "library_email": dispatch.survey.library.email,
            } for dispatch in Dispatch.objects.all()
        ]

        return render(request, 'libstat/dispatches.html', {"dispatches": dispatches})
