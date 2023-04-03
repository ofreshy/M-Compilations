"""
Test client to read
"""

import datetime
import json
import os

import requests


CLIENT_ID = "5e552813c154484eb1c62688ccd6d0e1"
CLIENT_SECRET = os.environ.get("SPOTIFY_CLIENT_SECRET")


AUTH_URL = 'https://accounts.spotify.com/api/token'

# auth_response = requests.post(AUTH_URL, {
#     'grant_type': 'client_credentials',
#     'client_id': CLIENT_ID,
#     'client_secret': CLIENT_SECRET,
# })
#
# # convert the response to JSON
# auth_response_data = auth_response.json()
#
# # save the access token
# print(auth_response_data)
# access_token = auth_response_data['access_token']
# print(access_token)
access_token = "BQBwAVI0vDEAItorKpVtgyupMUeBb_9Us145U35IIFbrcGgD5kIqUVxqi03Gi-TIsfFJHFOhsP6TlFvfMXmcZzAR7JjAs8kdXpAjVsESy6ToVJ2oCHlSvsWjHLETNsK_fiNHUaP_a4uHZcoBOnshUbAR9d_lMH4FR41DiC3WJadt8uv-Rvq8trcTrhKUxj7-YsJnuFMr9RTl4JyoCUAJ"
access_token = "BQC0aax1KUllPxsDXEEcl4v348Em8rbMmIzp56OkV28CkvXUbNJB"
access_token = "BQA42Qhvsyz15a9g1IWYUhqGkG1iqqI7pkvG60s_XD5SVaYggYDLKHhxe_PJth_94cUpxe4LyetRezu4oFezQd3EAE_-qgfwpWmDVn-uSaAXyeaySpZORyfm_Hlbq7cH-mizLDN4vSM3Ef_cL1HdB7J207jWRAF46BLjI69_jv9aPuIzcOwF1NlDjDkU-32FHmH6AlWmoTyQDIDVx5i4epM_9BeJAyU"
headers = {
    'Authorization': 'Bearer {token}'.format(token=access_token),
    'Contenty-Type': "Application/json",
}


url = "https://api.spotify.com/v1/audio-features?ids=13s6dCsNpSZflwVu2uzzPi%2C7u4YYDqgqEu7etjfwWy3u8"
r = requests.get(url, headers=headers)
print(r.json())
print()


def get_playlists():
    def _get_playlists(url):
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        return res.json()

    playlists = _get_playlists("https://api.spotify.com/v1/me/playlists?offset=0&limit=20")
    while url := playlists.get("next"):
        yield playlists["items"]
        playlists = _get_playlists(url)
    yield playlists["items"]


def filter_playlist_item(playlist_item):
    """

    """
    if playlist_item.get("owner", {}).get("display_name", "") != "ofreshy":
        return False
    playlist_name = playlist_item.get("name", "")
    if playlist_name.upper().startswith("ZZZ"):
        return False
    if playlist_name.startswith("0"):
        return False
    if playlist_name.upper().startswith("KIDS"):
        return False
    return True


def get_playlist_items(playlists):
    for playlist_item in playlists:
        yield (i for i in playlist_item if filter_playlist_item(i))


def get_track_items(playlist_item):

    def _get_tracks():
        res = requests.get(url, headers=headers)
        res.raise_for_status()
        return res.json()

    url = playlist_item["tracks"]["href"]
    tracks = _get_tracks()
    while url := tracks.get("next"):
        yield tracks["items"]
        tracks = _get_tracks()
    yield tracks["items"]


def get_tracks_and_playlist():
    for playlist_items in get_playlist_items(get_playlists()):
        for playlist_item in playlist_items:
            tracks = []
            for tr in get_track_items(playlist_item):
                tracks.extend(tr)
            yield playlist_item, tracks


def playlist_to_collection(playlist_item, tracks):
    def get_created_at_year():
        max_date = max(
            [a["added_at"] for a in tracks]
        )
        return datetime.datetime.strptime(max_date, "%Y-%m-%dT%H:%M:%SZ").year
    return {
      "name": playlist_item["name"],
      "created_year": get_created_at_year(),
      "description": playlist_item["description"],
      "tracks": [
          {
              "name": track["track"]["name"],
              "spotify_id": track["track"]["id"],
              "duration_ms": track["track"]["duration_ms"],
              "released_year": track["track"]["album"]["release_date"],
              "artists": [a["name"] for a in track["track"]["artists"]],
              "album": track["track"]["album"]["name"]
          }
          for track in tracks
        ]
    }








gen = get_tracks_and_playlist()
for i, (pi, tracks) in enumerate(gen):
    collection = playlist_to_collection(pi, tracks)
    with open(f"/tmp/{i}-{collection['name']}.json", "w") as f:
        f.write(json.dumps(collection))
    break

# # base URL of all Spotify API endpoints
# BASE_URL = 'https://api.spotify.com/v1/'
#
# # Track ID from the URI
# track_id = '6y0igZArWVi6Iz0rj35c1Y'
#
# # actual GET request with proper header
# r = requests.get(BASE_URL + 'audio-features/' + track_id, headers=headers)
# print(r.json())
#
# artist_id = '36QJpDe2go2KgaRleHCDTp'
#
# # pull all artists albums
# r = requests.get(BASE_URL + 'artists/' + artist_id + '/albums',
#                  headers=headers,
#                  params={'include_groups': 'album', 'limit': 50})
# d = r.json()
#
# print(d)
#
# for album in d['items']:
#     print(album['name'], ' --- ', album['release_date'])

url = "https://api.spotify.com/v1/audio-features?ids=13s6dCsNpSZflwVu2uzzPi="
requests.get(url, headers=headers)