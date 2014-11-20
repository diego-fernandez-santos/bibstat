# -*- coding: UTF-8 -*-
from datetime import datetime

import pytz
import re
from django import template
from libstat.models import Dispatch, Survey

from libstat.utils import target_groups_label


register = template.Library()


def utc_tz(value):
    return value.replace(tzinfo=pytz.utc) if value and isinstance(value, datetime) else value


def tg_label(value):
    return target_groups_label(value)


def srs_label(key):
    return next((status[1] for status in Survey.STATUSES if status[0] == key))


def access(value, arg):
    return value[arg]


def with_status(surveys, status):
    return [survey for survey in surveys if survey.status == status]


def with_library_type(surveys, library_type):
    return [survey for survey in surveys if survey.library.library_type == library_type]


def dispatches_count():
    return Dispatch.objects.count()


def split_into_number_and_body(description):
    if re.compile("^[0-9]+\.").match(description):
        return description.split(" ", 1)
    else:
        return ("", description)


register.filter('utc_tz', utc_tz)
register.filter('tg_label', tg_label)
register.filter('srs_label', srs_label)
register.filter('access', access)
register.filter('with_status', with_status)
register.filter('with_library_type', with_library_type)
register.filter('split_into_number_and_body', split_into_number_and_body)
register.simple_tag(dispatches_count)
