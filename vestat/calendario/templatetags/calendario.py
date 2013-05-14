# -*- encoding: utf-8 -*-
"""
templatetags pra gerar um calendário.

Fonte: http://williamjohnbert.com/2011/06/django-event-calendar-for-a-django-beginner/
"""

import logging
from calendar import HTMLCalendar
from django import template
from datetime import date
from itertools import groupby
import traceback

from django.utils.html import conditional_escape as esc

from vestat.calendario.views import named_month

register = template.Library()
logger = logging.getLogger("vestat")

day_abbr = [u"Seg", u"Ter", u"Qua", u"Qui", u"Sex", u"Sáb", u"Dom"]

def do_calendar(parser, token):
    """
    The template tag's syntax is { % reading_calendar year month events %}
    """

    try:
        tag_name, year, month, events = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires three arguments" % token.contents.split()[0])
    return CalendarNode(year, month, events)


class CalendarNode(template.Node):
    """
    Process a particular node in the template. Fail silently.
    """

    def __init__(self, year, month, events):
        try:
            self.year = template.Variable(year)
            self.month = template.Variable(month)
            self.events = template.Variable(events)
        except ValueError:
            raise template.TemplateSyntaxError

    def render(self, context):
        try:
            # Get the variables from the context so the method is thread-safe.
            my_events = self.events.resolve(context)
            my_year = self.year.resolve(context)
            my_month = self.month.resolve(context)
            cal = Calendar(my_events)
            return cal.formatmonth(int(my_year), int(my_month))
        except ValueError:
            logger.error(u"Erro ao renderizar calendário:")
            logger.error(traceback.format_exc())
            return
        except template.VariableDoesNotExist:
            logger.error(u"Erro ao renderizar calendário:")
            logger.error(traceback.format_exc())
            return


class Calendar(HTMLCalendar):
    """
    Overload Python's calendar.HTMLCalendar to add the appropriate event events to
    each day's table cell.
    """

    def __init__(self, events):
        super(Calendar, self).__init__()
        self.events = self.group_by_day(events)

    def formatday(self, day, weekday):
        if day != 0:
            cssclass = self.cssclasses[weekday]
            day_as_date = date(self.year, self.month, day)

            if date.today() == day_as_date:
                cssclass += u' today'

            if day_as_date in self.events:
                cssclass += u' filled'
                body = [u'<ul>']
                for event in self.events[day_as_date]:
                    body.append(u'<li title="{desc}">'.format(desc=event.description))
                    body.append(esc(event.text))
                    body.append(u'</li>')
                body.append(u'</ul>')
                return self.day_cell(cssclass, u'<span class="dayNumber">%d</span> %s' % (day, u''.join(body)))
            return self.day_cell(cssclass, u'<span class="dayNumberNos">%d</span>' % (day))
        return self.day_cell(u'noday', u'&nbsp;')

    def formatmonth(self, year, month):
        self.year, self.month = year, month
        return super(Calendar, self).formatmonth(year, month)

    def group_by_day(self, events):
        field = lambda event: event.date
        return dict(
            [(day, list(items)) for day, items in groupby(events, field)]
        )

    def day_cell(self, cssclass, body):
        return u'<td class="%s">%s</td>' % (cssclass, body)

    def formatweek(self, theweek):
        """
        Return a complete week as a table row.
        """
        s = u''.join(self.formatday(d, wd) for (d, wd) in theweek)
        return u'<tr>%s</tr>' % s

    def formatweekday(self, day):
        """
        Return a weekday name as a table header.
        """
        return u'<th class="%s">%s</th>' % (self.cssclasses[day], day_abbr[day])

    def formatweekheader(self):
        """
        Return a header for a week as a table row.
        """
        s = u''.join(self.formatweekday(i) for i in self.iterweekdays())
        return u'<tr>%s</tr>' % s

    def formatmonthname(self, theyear, themonth, withyear=True):
        """
        Return a month name as a table row.
        """
        if withyear:
            s = u'%s %s' % (named_month(themonth), theyear)
        else:
            s = u'%s' % month_name[themonth]
        return u'<tr><th colspan="7" class="month">%s</th></tr>' % s


# Register the template tag so it is available to templates
register.tag("calendar", do_calendar)

