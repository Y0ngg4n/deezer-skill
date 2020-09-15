from pydeezer import Deezer
import os

from pydeezer.constants import track_formats


def download_track(track_id, track_directory, arl):
    deezer = Deezer(arl=arl)
    track = deezer.get_track(track_id)
    download_path = os.path.join(track_directory, str(track_id))
    if not os.path.exists(track_directory):
        os.makedirs(track_directory)

    track["download"](download_path, quality=track_formats.MP3_320, filename=str(track_id))
    return os.path.join(download_path, str(track_id) + ".mp3")


def search_first_track(track_name, arl):
    deezer = Deezer(arl=arl)
    track_search_results = deezer.search_tracks(query=track_name, limit=1)
    try:
        return track_search_results[0]
    except IndexError:
        return None


def get_user_info(arl):
    deezer = Deezer(arl=arl)
    return deezer.user["name"]
