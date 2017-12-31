import datetime
import os
import urllib

import requests


class APIInterface(object):
    """
    This is an abstract object used to obtain events from an API
    """
    input_date_format = "%Y-%m-%d"  # the date format for specifying dates
    output_date_format = "%Y-%m-%d"  # the date format that the API uses for specifying dates

    @property
    def base_url(self):
        raise NotImplementedError()

    def _get_credentials(self, parameter, environment_variable):
        """
        Used to obtain an credentials from an input parameter when available
        with a fallback to a specified environment variable.
        """
        if parameter is not None:
            return parameter
        env_var = os.getenv(environment_variable)
        if env_var is None:
            raise ValueError(
                'unable to find envirionment variable {}'
                .format(environment_variable)
            )
        return env_var

    def get(self, path, params, headers=None):
        """
        Query the api

        Parameters
        ----------
        path: (str) the relative api path to query
        params: (list of tuples or dict) url parameters to append to the query
        headers: (dict) header parameters to include with the query

        Returns
        -------
        a json response from the API
        """
        url = "{}?{}".format(
            os.path.join(self.base_url, path),
            urllib.urlencode(params)
        )
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        return r.json()

    def _parse_date(self, date):
        """
        Parse a date string, or a date / datetime object, and output
        a date string in the format expected by the API
        """
        if isinstance(date, str):
            date = datetime.datetime.strptime(date, self.input_date_format)
        elif isinstance(date, (datetime.date, datetime.datetime)):
            pass
        else:
            raise ValueError(
                'expect datetime.date objects or string dates with format {}'
                .format(self.input_date_format)
            )
        return date.strftime(self.output_date_format)

    def events(self, per_page=50, page=1, **kwargs):
        """
        Abstract method:
            obtain raw events data from the API

        Parameters
        ----------
        per_page: (int) the number of events to return in a page
        page: (int) the page index to return

        Returns
        -------
        a list of raw event objects provided by the API
        """
        raise NotImplementedError()

    def _parse_event(self, event):
        """
        Abstract method:
            given a raw event object obtained from the API,
            parse that object into an `Event` object from
            the data_model

        Parameters
        ----------
        event: a raw event object provided by the API

        Returns
        -------
        an `Event` object.
        """
        raise NotImplementedError()

    def parsed_events(self,
                      limit=250,
                      per_page=50,
                      **kwargs):
        """
        Query the API for events and return a list of `Event` objects

        Parameters
        ----------
        limit (int): the maximum number of responses to return
        per_page (int): the maximum number of responses to request
            on each API call
        **kwargs: additional optiona accepted by self.events

        Returns
        -------
        A list of `Event` objects
        """
        events = []
        page = 1
        while True:
            e = self.events(per_page=per_page, page=page, **kwargs)
            events.extend(e)
            if len(events) >= limit:
                events = events[:limit]
                break
            elif len(e) >= per_page:
                page += 1
                continue
            else:
                break

        return [
            self._parse_event(event)
            for event in events
        ]
