"""Template filters for rendering plain-text lesson notes safely."""

import re

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()

_CALLOUT = re.compile(r"^(warning|tip|example|note|remember)\s*:\s*(.+)$", re.I)


@register.filter(name="lesson_notes")
def lesson_notes(value):
    """Turn the existing plain-text lesson body into structured HTML.

    Every line is escaped before being wrapped in markup. Only the small set of
    tags emitted here is marked safe, so lesson authors cannot inject HTML.
    """
    if not value:
        return ""

    output = []
    in_list = False

    def close_list():
        nonlocal in_list
        if in_list:
            output.append("</ul>")
            in_list = False

    for raw_line in value.splitlines():
        line = raw_line.strip()
        if not line:
            close_list()
            continue

        callout = _CALLOUT.match(line)
        if callout:
            close_list()
            kind = callout.group(1).lower()
            text = callout.group(2)
            output.append(
                '<div class="cq-note-callout cq-callout-'
                + kind
                + '"><strong>'
                + kind.title()
                + ":</strong> "
                + escape(text)
                + "</div>"
            )
            continue

        if line.startswith("•"):
            if not in_list:
                output.append('<ul class="cq-note-list">')
                in_list = True
            output.append("<li>" + escape(line.lstrip("•").strip()) + "</li>")
            continue

        is_heading = (
            line.endswith(":")
            or (len(line) <= 40 and not line.endswith((".", "?", "!", ":")))
        )
        close_list()
        if is_heading:
            output.append("<h3>" + escape(line.rstrip(":")) + "</h3>")
        else:
            output.append("<p>" + escape(line) + "</p>")

    close_list()
    return mark_safe("".join(output))
