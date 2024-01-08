"""
The liked playlist is used to add songs that I'd like to add to other playlists

Once a song from liked is in a finalised playlist then it can be removed from that liked playlist

Script here does exactly that

Read all songs from local storage
Read the songs from liked playlist
Removed all songs that are in both
"""
import integrations.spotify.client
from integrations.spotify import models
from musik_lib import collections


def main():
    print("Start Prune Saved Tracks")

    client = integrations.spotify.client.SpotifyClient.make_default()
    saved_tracks = client.saved_tracks()

    local_collections = collections.get_local_spotify_collections_content()
    local_tracks_by_track_id = {
        track["spotify_id"]: track
        for collection in local_collections
        for track in collection["tracks"]
    }

    track_name_by_track_id_to_remove = {
        track["id"]: track["name"] for track in saved_tracks
        if track["id"] in local_tracks_by_track_id
    }
    if track_name_by_track_id_to_remove:
        print(f"Removing {len(track_name_by_track_id_to_remove)} from the liked playlist. Removed tracks are")
        print(",".join(list(track_name_by_track_id_to_remove.values())))

        client.delete_from_saved_tracks(
            list(track_name_by_track_id_to_remove.keys())
        )
    else:
        print("Nothing to remove")

    print("Finish Prune Saved Tracks")


if __name__ == '__main__':
    main()
