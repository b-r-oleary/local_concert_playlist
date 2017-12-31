import datetime

from local_concert_playlist.api.base import APIInterface
from local_concert_playlist.model import (
    Event,
    Performer,
    Venue
)


class OhMyRocknessAPI(APIInterface):
    """
    """
    base_url = "https://www.ohmyrockness.com/api"
    output_date_format = "%m-%d-%Y"  # this API uses this format for specifying date ranges

    def __init__(self, token=None, user_agent=None):
        self.token = self._get_credentials(
            token,
            'OHMYROCKNESS_TOKEN'
        )
        self.user_agent = self._get_credentials(
            user_agent,
            'OHMYROCKNESS_USER_AGENT'
        )

    def get(self, path, params, headers=None):
        if headers is None:
            headers = {}
        headers.update({
            'user-agent': self.user_agent,
            'authorization': 'Token token="{}"'.format(self.token)
        })
        return super(OhMyRocknessAPI, self).get(path, params, headers=headers)

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
