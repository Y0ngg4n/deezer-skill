from pydeezer import Deezer
import os

from pydeezer.constants import track_formats

track_directory = os.path.join("music", "track")
arl = "the_arl_for_testing_hardcoded"


def download_track(track_id, arl):
    deezer = Deezer(arl=arl)
    track = deezer.get_track(track_id)
    track["download"](os.path.join(track_directory, str(track_id)), quality=track_formats.MP3_320)


def search_first_track(track_name, arl):
    deezer = Deezer(arl=arl)
    track_search_results = deezer.search_tracks(query=track_name, limit=1)
    try:
        return track_search_results[0]["id"]
    except IndexError:
        return None

def get_user_info(arl):
    deezer = Deezer(arl=arl)
    return deezer.user["name"]
