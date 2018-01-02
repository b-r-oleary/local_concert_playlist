# Discovering artists who are touring near you

As part of an annual end-of-year tradition I have been scouring the "best music of 2017" lists on [npr music](https://www.npr.org/series/534681872/best-music-of-2017), [pitchfork](https://pitchfork.com/topics/the-best-music-of-2017/), and [spotify](https://open.spotify.com/user/spotifyyearinmusic/playlist/2xKlsGov0EC2fhl6uXDgWZ).
This practice is mostly a futile attempt to try to keep up with new music, most of which probably has eluded me over the course of the past year. Staying up to date with new music can be a time consuming hobby, if not a full time job. However this practice serves a second, arguably more important, purpose: to ensure that I don't miss out on upcoming concerts that I might retroactively regret missing. In a word, FOMO ([... yes it is a word](https://www.merriam-webster.com/dictionary/FOMO)). 

So instead of following the normal path of scouring the 'best music' lists, identifying bands of interest, and cross referencing with upcoming concerts, I decided to automate the creation of Spotify playlists associated with performers who will be touring nearby in upcoming concerts. The [local_concert_playlist](https://github.com/b-r-oleary/local_concert_playlist) repository on github was built as a library that can be used to build such playlists. This library provides objects that facilitate obtaining lists of upcoming events from the Spotify API or the OhMyRockness API, and then facilitate the selection of tracks by artists who are performing at these events that can then be uploaded into a Spotify playlist.

### Setup

In order to create your own playlists using this library, the setup requires two steps - creating your local dev environment and obtaining API credentials. The setup of the local dev environment is pretty straight forward:

```bash
# clone the repository and install the python package requirements
git clone git@github.com:b-r-oleary/local_concert_playlist.git
cd local_concert_playlist
pip install -r requirements.txt
cp .env.sample .env
```

In order to access the Spotify, SeatGeek, and OhMyRockness API's we will need to obtain API credentials. These environment variables can be set in the `.env` file for convenience, from which we can `source` the environment. In order to obtain these credentials you will need to follow these steps:

- **Spotify API credentials**: Create an account with spotify, if you don't already have one, and set your username in the environment variable `SPOTIFY_USERNAME`. [Create a spotify "app" here](https://beta.developer.spotify.com/dashboard/applications). The client id and client secret should be set in the `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` environment variables respectively. You will then need to add a redirect url that will be authorized for redirecting after your app has received permission to create playlists on behalf of your spotify username. This can be set by clicking "edit settings" and then entering the URL under the "Redirect URIs" heading. This url should be set in the environment variable `SPOTIFY_REDIRECT_URI`.

- **SeatGeek API credentials**: SeatGeek can be used as a source of live events. You will need to create an account with SeatGeek, if you don't already have one. Then [create an app that is associated with this account](https://seatgeek.com/account/develop). The client id and client secret associated with this app should be set in the `SEATGEEK_CLIENT_ID` and `SEATGEEK_CLIENT_SECRET` environment variables respectively.

- **OhMyRockness API credentials**: OhMyRockness can be used as a source of live events in New York City. OhMyRockness does not technically have a developer API like the other sites, but they do appear to have an API that powers their website. Access to this API appears to require a "token" which is included in the API request headers. You can obtain one of these by navigating to [ohmyrockness.com](ohmyrockness.com) with the developer tools window open. While the page is loading the site makes a call to an endpoint that starts with `show.json`. A token can be found in the `authorization` field in the headers associated with this request. This token can be set in the `OHMYROCKENESS_TOKEN` to obtain access to this API.

### Using the library

The typical workflow for constructing a playlist includes:
- obtaining a subset of upcoming events from an external API (using `SeatGeekAPI.parsed_events` or `OhMyRocknessAPI.parsed_events`)
- filtering the list of events further (using `filter_events`)
- selecting tracks on Spotify corresponding to performers that are associated with the upcoming events (using `SpotifyPlaylist.select_tracks_for_events`)
- creating a playlist using those tracks (using `SpotifyPlaylist.create_playlist`)

A simple example is provided here:

```python
from local_concert_playlist import OhMyRocknessAPI, SpotifyPlaylist

events = OhMyRocknessAPI().parsed_events(limit=100)
p = SpotifyPlaylist()
tracks = p.select_tracks_for_events(events, max_tracks=50)
p.create_playlist('Trial Playlist', tracks)
```

Going beyond this simple example, many options are provided to filter the events returned by the API, to filter events after they are returned from the API, and to select tracks corresponding to event performers. Keep in mind that for each performer associated with concert events the `select_tracks_for_events` method performs a query against Spotify to identify the performer and identify tracks associated with this performer and that this step can take a considerable amount of time if there are many performers.
