# -*- encoding: utf-8 -*-
"""
Views pra gerar um calendário e navegar através dos meses/anos.

Adaptado de: http://williamjohnbert.com/2011/06/django-event-calendar-for-a-django-beginner/
"""

from datetime import date
from calendar import monthrange
import logging

from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.views.generic.base import View
from django.core.urlresolvers import reverse

from calendario import get_events
from forms import CalendarForm

logger = logging.getLogger("vestat")


class EventsCalendarView(View):
    """
    View que exibe os dias e eventos de um mês do calendário.
    """

    def named_month(month_number):
        """
        Return the name of the month, given the number.
        """

        return date(1900, month_number, 1).strftime("%B").decode("latin-1")

    template_name = "cal_template.html"

    def post(self, request, year, month):
        """
        Extrai o formulário `forms.CalendarForm` do POST. Se o
        formulário for válido, redireciona pra URL correspondente ao seu
        mês/ano. Caso não seja, repassa o formulário inválido e o
        mês/ano atuais pra `EventsCalendarView.render`.

        Argumentos:
            - request
            - year: string; o ano passado pela URL
            - month: string; o mês passado pela URL
        """

        form = CalendarForm(request.POST)
        if form.is_valid():
            year = "{0:04d}".format(int(form.cleaned_data['year']))
            month = "{0:02d}".format(int(form.cleaned_data['month']))
            url = reverse("calendario:events_calendar", args=(year, month))
            return redirect(url)
        else:
            return self.render(request, year, month, form)

    def get(self, request, year, month):
        """
        Cria um formulário vazio e o repassa pra
        `EventsCalendarView.render`, junto com os outros argumentos.

        Argumentos:
            - request
            - year: string; o ano passado pela URL
            - month: string; o mês passado pela URL
        """

        form = CalendarForm()
        return self.render(request, year, month, form)

    def render(self, request, year, month, form):
        """
        Exibe os dias e eventos do mês/ano passados pela URL, e o formulário
        passado pelo método `get` ou `post`.
        """

        my_year = int(year)
        my_month = int(month)
        my_calendar_from_month = date(my_year, my_month, 1)
        my_calendar_to_month = date(my_year, my_month, monthrange(my_year, my_month)[1])

        my_events = get_events(my_calendar_from_month, my_calendar_to_month)

        # Calculate values for the calendar controls. 1-indexed (Jan = 1)
        my_previous_year = my_year
        my_previous_month = my_month - 1

        if my_previous_month == 0:
            my_previous_year = my_year - 1
            my_previous_month = 12

        my_next_year = my_year
        my_next_month = my_month + 1

        if my_next_month == 13:
            my_next_year = my_year + 1
            my_next_month = 1

        my_year_after_this = my_year + 1
        my_year_before_this = my_year - 1

        return render_to_response("cal_template.html", {
            "form": form,
            "events": my_events,
            "month": my_month,
            "month_name": named_month(my_month),
            "year": my_year,
            "previous_month": "{0:02d}".format(my_previous_month),
            "previous_month_name": named_month(my_previous_month),
            "previous_year": "{0:04d}".format(my_previous_year),
            "next_month": "{0:02d}".format(my_next_month),
            "next_month_name": named_month(my_next_month),
            "next_year": "{0:04d}".format(my_next_year),
            "year_before_this": my_year_before_this,
            "year_after_this": my_year_after_this,
        }, context_instance=RequestContext(request))
