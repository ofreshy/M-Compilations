"""
The liked playlist is used to add songs that I'd like to add to other playlists

Once a song from liked is in a finalised playlist then it can be removed from that liked playlist

Script here does exactly that

Read all songs from local storage
Read the songs from liked playlist
Removed all songs that are in both
"""
from integrations.spotify.client import SpotifyClient
from musik_lib import collections


def _get_tracks_to_remove(remote_tracks, local_collections):
    local_tracks_by_track_id = {
        track["spotify_id"]: track
        for collection in local_collections
        for track in collection["tracks"]
    }
    track_name_by_track_id_to_remove = {
        track["id"]: track["name"] for track in remote_tracks
        if track["id"] in local_tracks_by_track_id
    }
    return track_name_by_track_id_to_remove


def main():
    print("Start Prune Saved Tracks")

    client = SpotifyClient.make_default()

    saved_tracks = client.saved_tracks()
    local_collections = collections.get_local_spotify_collections_content()
    track_name_by_track_id_to_remove = _get_tracks_to_remove(
        remote_tracks=saved_tracks,
        local_collections=local_collections,
    )

    if track_name_by_track_id_to_remove:
        print(f"Removing {len(track_name_by_track_id_to_remove)} from the liked playlist. Removed tracks are")
        print(",\n".join(list(track_name_by_track_id_to_remove.values())))

        client.delete_from_saved_tracks(
            list(track_name_by_track_id_to_remove.keys())
        )
    else:
        print("Nothing to remove")

    print("Finish Prune Saved Tracks")


if __name__ == '__main__':
    main()
