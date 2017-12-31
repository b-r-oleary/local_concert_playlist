"""
This is a small library that makes it easy to build
event filters
"""


class Filter(object):
    def __call__(self, event):
        raise NotImplementedError()


class IncludeExclude(Filter):
    def __init__(self, get_attr, includes=None, excludes=None):
        self.get_attr = get_attr
        self.includes = self._parse_inputs(includes)
        self.excludes = self._parse_inputs(excludes)

    def _parse_inputs(self, var):
        if var is None:
            return None
        if isinstance(var, (list, tuple, set)):
            return set(var)
        else:
            return set([var])

    def __call__(self, event):
        attrs = self.get_attr(event)
        output = True
        if self.includes is not None:
            output &= any(
                attr in self.includes
                for attr in attrs
            )
        if self.excludes is not None:
            output &= not any(
                attr in self.excludes
                for attr in attrs
            )
        return output


def create_filter(get_attr):
    class CustomFilter(IncludeExclude):
        def __init__(self, includes=None, excludes=None):
            super(CustomFilter, self).__init__(
                get_attr,
                includes=includes,
                excludes=excludes
            )
    return CustomFilter


class FilterCombination(Filter):
    def __init__(self, *filters):
        self.filters = filters

    def __call__(self, event):
        return all(
            f(event) for f in self.filters
        )


def filter_events(events,
                  include_venue=None,
                  exclude_venue=None,
                  include_genre=None,
                  exclude_genre=None,
                  include_city=None,
                  exclude_city=None,
                  include_day_of_week=None,
                  exclude_day_of_week=None):

    venue_filter = create_filter(lambda event: [event.venue.name])
    genre_filter = create_filter(lambda event: [
        genre.name for performer in event.performers
        for genre in performer.genres
    ])
    city_filter = create_filter(lambda event: [event.venue.city])
    day_of_week_filter = create_filter(
        lambda event: [event.datetime_local.weekday()]
    )

    event_filter = FilterCombination(
        venue_filter(includes=include_venue,
                     excludes=exclude_venue),
        genre_filter(includes=include_genre,
                     excludes=exclude_genre),
        city_filter(includes=include_city,
                    excludes=exclude_city),
        day_of_week_filter(includes=include_day_of_week,
                           excludes=exclude_day_of_week)
    )

    return filter(event_filter, events)
