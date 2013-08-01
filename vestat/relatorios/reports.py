# -*- encoding: utf-8 -*-

"""A report generator for Django querysets.

Defined classes:

- `Table`, a table generator, based on `tablib.Dataset`.
- `TableField`, a field of a `Table`.
- `Report`, the actual report generator.
"""

import types

from django.template.defaultfilters import slugify
from django import forms
import tablib

class TableField():
    """A field for a :class:`Table`. Encapsulates the field header, the slug
    and the field HTML classes."""

    def __init__(self, header, slug=None, classes=[]):
        """Initialize a :class:`TableField`.

        If `slug` is not provided, `self.slug` is set automatically
        based on `self.header`."""

        self.header = header
        self.slug = slug or slugify(header)
        self.classes = classes


class Table(tablib.Dataset):
    """A extension of `tablib.Dataset` that has fields' slugs and HTML classes,
    and processes data that it is fed through a function provided at
    initialization."""

    def __init__(self, fields, process_data, *args, **kwargs):
        """Initialize a :class:`Table` object; extends
        :class:`tablib.Dataset.__init()__`.

        :Parameters:
            - `fields`: list of :class:`TableField` objects.
            - `process_data`: function that processes data, creating table
              rows. May accept any number of parameters, and should use these
              parameters to create `tablib.Dataset` rows."""

        super(Table, self).__init__(*args, **kwargs)
        self.fields = fields
        self._process_data = types.MethodType(process_data, self, Table)
        self.headers = [f.header for f in self.fields]

    def process_data(self, *args, **kwargs):
        """Processes data, creating the corresponding table rows.

        Wrapper for the processing function passed on the initialization."""
        return self._process_data(*args, **kwargs)


class Report():
    """A report that filters data and creates tables based on it.

    Filters should be :class:`FilterForm` objects, and tables should be 
    :class:`Table` objects. Both should know how to deal with the data that the 
    report is fed.
    """
    def __init__(self, data=None, filters=[], tables=[]):
        """Initialize a :class:`Report` object and processes `data`, filtering 
        it and populating `tables`'s rows.

        :Parameters:
            - `data`: the data that the report should based on, in a format 
              that should be handled by the filters and tables.
            - `filters`: a list of :class:`FilterForm` objects.
            - `tables`: a list of :class:`Table` objects.
        """
        self.data = data
        self.filters = filters
        self.tables = tables
        self.generate_report()

    def generate_report(self):
        self.apply_filters()
        self.generate_tables()

    def add_data(self, data):
        """Adds data and recreates the report."""
        if self.data is None:
            self.data = data
        else:
            self.data += data
        self.generate_report()

    def add_filter(self, filter_):
        """Adds a filter and recreates the report."""
        self.filters.append(filter_)
        self.generate_report()

    def add_table(self, table):
        """Adds a table and recreates the report."""
        self.tables.append(table)
        self.generate_report()

    def apply_filters(self):
        """Applies filters to the provided data and stores the result internally."""
        self.filtered_data = self.data
        for filter_ in self.filters:
            self.filtered_data = filter_.filter(self.filtered_data)

    def generate_tables(self):
        """Removes all rows from table and creates new rows, based on the filtered data."""
        for table in self.tables:
            # cleaning the table but letting the headers intact
            headers = table.headers
            table.wipe()
            table.headers = headers

            table.process_data(self.filtered_data)
