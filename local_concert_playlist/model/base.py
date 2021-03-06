"""
These objects are used to create a uniform data model
for events from multiple APIs
"""


class Event(object):

    def __init__(self,
                 source,
                 source_id,
                 name,
                 datetime_local,
                 venue,
                 performers):

        self.source = source
        self.source_id = source_id
        self.name = name
        self.datetime_local = datetime_local
        self.venue = venue
        self.performers = performers


class Performer(object):

    def __init__(self,
                 source,
                 source_id,
                 name,
                 genres):

        self.source = source
        self.source_id = source_id
        self.name = name
        self.genres = genres


class Venue(object):

    def __init__(self,
                 source,
                 source_id,
                 name,
                 address,
                 city):

        self.source = source
        self.source_id = source_id
        self.name = name
        self.address = address
        self.city = city


class Genre(object):

    def __init__(self,
                 source,
                 source_id,
                 name):

        self.source = source
        self.source_id = source_id
        self.name = name
