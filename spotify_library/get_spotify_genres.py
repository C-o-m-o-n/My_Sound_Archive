import requests

from spotify_auth.models import SpotifyToken


def spotify_get_artists_genres(artists_uris, request):

    user = SpotifyToken.objects.get(user = request.user)
    access_token = user.access_token

    artists_uris_genres = []

    n = len(artists_uris)//50
    a = 0
    b = 50
    for _ in range(n):
        artists_uris_50items = artists_uris[a:b]

        spotify_response_json, status_code = spotify_artists(
            artists_uris_50items, access_token)
        print(status_code)
        spotify_response = spotify_response_json.json()
        artists_genres_50items = spotify_response["artists"]

        for artist in artists_genres_50items:
            artists_uris_genres.append(
                (artist["uri"], tuple(artist["genres"]))
            )
        a += 50
        b += 50

    artists_uris_therest = artists_uris[n*50:]
    spotify_response_json, status_code = spotify_artists(
        artists_uris_therest, access_token)
    spotify_response = spotify_response_json.json()
    artists_genres_therest = spotify_response["artists"]

    for artist in artists_genres_therest:
        artists_uris_genres.append((artist["uri"], tuple(artist["genres"])))
    return artists_uris_genres


def spotify_artists(artists_uris_50items, access_token):

    base_url = 'https://api.spotify.com/v1/artists'
    url = base_url + '?ids=' + ",".join(artists_uris_50items)
    headers = {
        'Authorization': 'Bearer ' + access_token
    }
    spotify_response_json = requests.get(url, headers=headers)
    status_code = spotify_response_json.status_code
    return spotify_response_json, status_code
