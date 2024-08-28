import difflib
import re
from typing import List, Optional, Iterator, Dict

import spotipy
from spotipy import SpotifyOAuth

from integrations.spotify.models import SpotifyTrack


NUM_SEARCH_ITEMS = 15
AND_REGEX = re.compile(" & | and |, | feat | featuring | feat\\. | מארח את ", re.IGNORECASE)


class SpotifyClient:
    """
    Thin wrapper for spotipy client
    so can get resources in a streaming fashion instead of bulk
    """
    client: spotipy.Spotify
    limit: int

    @classmethod
    def make_default(cls, limit=50, extra_scope=None):
        base_scope = [
            "user-read-private",
            "user-read-email",
            "user-library-read",
            "user-library-modify",
        ]
        extra_scope = extra_scope or []
        scope = base_scope + extra_scope
        return cls(
            client=spotipy.Spotify(
                client_credentials_manager=SpotifyOAuth(
                    scope=scope,
                ),
            ),
            limit=limit,
        )

    def __init__(self, client: spotipy.Spotify, limit):
        self.client = client
        self.limit = limit

    def me(self):
        return self.client.me()

    def user_id(self):
        return self.me()["id"]

    def saved_tracks(self):
        """
        Returns an iterator over saved tracks
        """
        def gen_items(saved_items):
            return (i["track"] for i in saved_items)

        response = self.client.current_user_saved_tracks(
            limit=self.limit,
        )
        while response["next"] is not None:
            yield from gen_items(response["items"])
            response = self.client.next(response)
        yield from gen_items(response["items"])

    def delete_from_saved_tracks(self, tracks: List[str]):
        """
        Takes a list of track ids or track urls
        """
        return self.client.current_user_saved_tracks_delete(
            tracks
        )

    def search_track(self, track_name, artist_name, duration: str) -> Optional[SpotifyTrack]:
        def gen_items():
            response = self.client.search(
                q=f"{track_name}, {artist_name}",
                type="track",
                limit=NUM_SEARCH_ITEMS,
            )
            items = response.get("tracks", {}).get("items", [])
            yield from (i for i in items)

            if len(artist_names := artist_name_to_list(artist_name)) > 1:
                first_artist_name = artist_names[0]
                response = self.client.search(
                    q=f"{track_name}, {first_artist_name}",
                    type="track",
                    limit=NUM_SEARCH_ITEMS,
                )
                items = response.get("tracks", {}).get("items", [])
                yield from (i for i in items)

        track_filter = make_track_filter(track_name, artist_name, duration)
        found_item = next(filter(track_filter, gen_items()), None)
        if not found_item:
            raise ValueError(
                f"Did not find a match for {track_name}, {artist_name} in items"
            )
        spotify_track = SpotifyTrack.from_spotify_api(found_item)
        print(
            f"Found a match for {track_name}, {artist_name} : {spotify_track}"
        )

        return spotify_track

    def playlists(self) -> Iterator[Dict]:
        """
        Returns an iterator of playlist items dict;
        Buffering the API call into chunks of items
        """
        def gen_items(playlist_items):
            return (i for i in playlist_items)

        playlists = self.client.user_playlists(
                user=self.me()["id"],
                limit=self.limit,
            )
        while playlists["next"] is not None:
            yield from gen_items(playlists["items"])
            playlists = self.client.next(playlists)
        yield from gen_items(playlists["items"])

    def playlist_items(self, playlist) -> Iterator[Dict]:
        """
        Returns an iterator of playlist items (Tracks)
        """
        def gen_items(items):
            return (i for i in items)

        playlist_items = self.client.playlist_items(
            playlist_id=playlist["id"],
            limit=self.limit,
        )
        while playlist_items["next"] is not None:
            yield from gen_items(playlist_items["items"])
            playlist_items = self.client.next(playlist_items)
        yield from gen_items(playlist_items["items"])

    def audio_features(self, track_id: str):
        return self.client.audio_features(track_id)[0]

    def create_playlist(self, playlist_name: str, uris: List[str], description: Optional[str]):
        """
        playlist name is unique in my collections so use this to understand whether this is a
        create or update
        """
        response = self.client.user_playlist_create(
            user=self.user_id(),
            name=playlist_name,
            description=description,
        )
        if response is None:
            raise

        response = self.client.playlist_add_items(
            playlist_id=response["id"],
            items=uris,
        )
        if response is None:
            raise

        return response

    def update_playlist(self, playlist_id: str, uris: List[str], collection: Dict):
        res = self.client.playlist_replace_items(
            playlist_id=playlist_id,
            items=uris,
        )
        if res is None:
            raise

        res = self.client.playlist_change_details(
            playlist_id=playlist_id,
            description=collection["description"],
        )


def make_track_filter(track_name: str, artist_name: str, duration: str):
    def duration_to_ms():
        duration_parts = duration.split(":")
        len_duration = len(duration_parts)
        if len_duration == 3:
            hours, minutes, seconds = duration_parts
        elif len_duration == 2:
            hours, minutes, seconds = ['0'] + duration_parts
        else:
            raise ValueError(f"Failed to parse duration -> {duration}")

        return (
                int(hours) * 3600 + int(minutes) * 60 + int(seconds)
        ) * 1000

    origin_artists = artist_name_to_list(artist_name)
    duration_in_ms = duration_to_ms()
    duration_min = duration_in_ms * 0.9
    duration_max = duration_in_ms * 1.1
    track_name_lower = track_name.lower()

    def type_filter(_item):
        if _item["type"] == "track":
            return True
        print(f"False. not type track item: {_item}")
        return False

    def similar_name_filter(_item) -> bool:
        item_name: str = _item["name"].lower()
        if "remaster" in item_name and "-" in item_name:
            parts = item_name.split("-")
            item_name = parts[0].strip()
        similar_score = difflib.SequenceMatcher(
            a=item_name,
            b=track_name_lower,
        ).ratio()
        if similar_score >= 0.85:
            return True

        print(f"False. track name {track_name_lower} dissimilar to item name {item_name}")
        return False

    def artist_name_filter(_item):
        artists_names_in_response = [
            a["name"].lower() for a in _item["artists"]
        ]
        artist_in_response = any(
            [
                artist in artists_names_in_response
                for artist in origin_artists
            ]
        )
        if artist_in_response:
            return True
        # Fuzzy match now
        _item_artists = "".join(artists_names_in_response)
        similar_score = difflib.SequenceMatcher(
            a=_item_artists.lower(),
            b=artist_name.lower(),
        ).ratio()
        if similar_score >= 0.9:
            return True

        print(
            f"Can't find origin artist {origin_artists} in  {artists_names_in_response}"
        )
        return False

    def make_duration_filter(_item):
        _item_duration = _item["duration_ms"]
        if duration_min <= _item_duration <= duration_max:
            return True
        print(
            f"Item name {_item['name']} duration {_item_duration} is not in bounds ({duration_min}, {duration_max})"
        )
        return False

    all_filters = (
        type_filter,
        similar_name_filter,
        artist_name_filter,
        make_duration_filter,
    )

    def filter_all(_item):
        return all(
            (
                f(_item)
                for f
                in all_filters
            )
        )

    return filter_all


def artist_name_to_list(artist_names: str):
    return [
        name.strip().replace("\\&", "&").lower()
        for name
        in AND_REGEX.split(artist_names)
    ]
