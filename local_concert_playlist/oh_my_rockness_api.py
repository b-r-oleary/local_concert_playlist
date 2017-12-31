import datetime
import os

import requests

from local_concert_playlist.data_model import (
    Genre,
    Event,
    Performer,
    Venue
)


class OhMyRocknessAPI(object):
    base_url = "https://www.ohmyrockness.com/api"

    def __init__(self, token, user_agent):
        self.token = token
        self.user_agent = user_agent

    def get(self, path, params):
        headers = {
            'user-agent': self.user_agent,
            'authorization': 'Token token="{}"'.format(self.token)
        }
        url = "{}?{}".format(
            os.path.join(self.base_url, path),
            urllib.urlencode(params)
        )
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        return r.json()

    def _parse_date(self, date):
        input_date_format = "%Y-%m-%d"
        output_date_format = "%m-%d-%Y"
        if isinstance(date, str):
            date = datetime.datetime.strptime(date, input_date_format)
        elif isinstance(date, (datetime.date, datetime.datetime)):
            pass
        else:
            raise ValueError(
                'expect datetime.date objects or string dates with format {}'
                .format(input_date_format)
            )
        return date.strftime(output_date_format)

    def events(self,
               start_date=None,
               end_date=None,
               index=True,
               regioned=1,
               page=1,
               per_page=50):

        params = []
        if start_date is not None:
            params.append(('daterange[from]', self._parse_date(start_date)))
        if end_date is not None:
            params.append(('daterange[until]', self._parse_date(end_date)))
        if index:
            params.append(('index', 'true'))
        params.append(('page', page))
        params.append(('per', per_page))
        params.append(('regioned', regioned))

        return self.get('shows.json', params)

    def _parse_event(self, event):
        source = self.__class__.__name__
        event_name = ', '.join([
            band['name'] for band in event['cached_bands']
        ])
        datetime_utc = datetime.datetime.strptime(
            '-'.join(event['starts_at'].split('-')[:-1]),
            '%Y-%m-%dT%H:%M:%S'
        )
        performers = [
            Performer(
                source,
                performer['id'],
                performer['name'],
                []
            )
            for performer in event['cached_bands']
        ]
        venue = Venue(
            source,
            event['venue']['id'],
            event['venue']['name'],
            event['venue']['full_address'],
            event['venue']['full_address'].split('\n')[-1].split(',')[0]
        )
        return Event(
            source,
            event['id'],
            event_name,
            datetime_utc,
            venue,
            performers
        )

    def parsed_events(self,
                      limit=250,
                      per_page=50,
                      **kwargs):
        events = []
        page = 1
        while True:
            e = self.events(per_page=50, page=page, **kwargs)
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
