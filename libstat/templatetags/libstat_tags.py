# -*- coding: UTF-8 -*-
from datetime import datetime
import json
import textwrap

import pytz
import re
from django import template
from bibstat import settings
from libstat.models import Dispatch, Survey
import locale

from libstat.utils import targetGroups, ALL_TARGET_GROUPS_label
from data.municipalities import municipalities

register = template.Library()


def utc_tz(value):
    return value.replace(tzinfo=pytz.utc) if value and isinstance(value, datetime) else value


def tg_label(value):
    display_names = []
    if value:
        if isinstance(value, list):
            if set(value) == set(targetGroups.keys()):
                display_names.append(ALL_TARGET_GROUPS_label)
            else:
                for tg in value:
                    if tg in targetGroups:
                        display_names.append(targetGroups[tg])
        else:
            if value in targetGroups:
                display_names.append(targetGroups[value])
    return ", ".join(display_names)


def srs_label(key):
    return next((status[1] for status in Survey.STATUSES if status[0] == key))


def access(value, arg):
    try:
        return value[arg]
    except KeyError:
        return None


def dispatches_count():
    return Dispatch.objects.count()


def split_into_number_and_body(description):
    if re.compile("^[0-9]+\.").match(description):
        return description.split(" ", 1)
    else:
        return ("", description)


def municipality_name(municipality_code):
    return municipalities.get(municipality_code, None)


def as_json(o):
    return json.dumps(o)


def analytics_enabled(_):
    return settings.ANALYTICS_ENABLED


def debug_enabled(_):
    return settings.DEBUG


def format_number(number, digits=1):
    if number == int(number):
        number_format = "%d"
    else:
        number_format = "%.{}f".format(digits)

    locale.setlocale(locale.LC_NUMERIC, 'sv_SE')
    return locale.format(number_format, number, grouping=True)


def format_email(email, limit=30):
    if len(email) <= limit:
        return email

    return email[:limit - 3] + "..."


def footer():
    return "&copy; Kungliga Biblioteket 2014-" + str(datetime.now().year)


@register.filter
def partition(thelist, n):
    """
    Break a list into ``n`` pieces. The last list may be larger than the rest if
    the list doesn't break cleanly. That is::

        >>> l = range(10)

        >>> partition(l, 2)
        [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]

        >>> partition(l, 3)
        [[0, 1, 2], [3, 4, 5], [6, 7, 8, 9]]

        >>> partition(l, 4)
        [[0, 1], [2, 3], [4, 5], [6, 7, 8, 9]]

        >>> partition(l, 5)
        [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]

    """
    try:
        n = int(n)
        thelist = list(thelist)
    except (ValueError, TypeError):
        return [thelist]
    p = len(thelist) / n
    return [thelist[p * i:p * (i + 1)] for i in range(n - 1)] + [thelist[p * (i + 1):]]


@register.filter
def show_in_chart(rows):
    rows = [row for row in rows if "show_in_chart" in row]

    for row in rows:
        row["label"] = "<br>".join(textwrap.wrap(row["label"], 50))

    return rows


register.filter('utc_tz', utc_tz)
register.filter('tg_label', tg_label)
register.filter('srs_label', srs_label)
register.filter('access', access)
register.filter('municipality_name', municipality_name)
register.filter('split_into_number_and_body', split_into_number_and_body)
register.filter('as_json', as_json)
register.filter('analytics_enabled', analytics_enabled)
register.filter('debug_enabled', debug_enabled)
register.filter('format_number', format_number)
register.filter('format_email', format_email)
register.simple_tag(dispatches_count)
register.simple_tag(footer)
