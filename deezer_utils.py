from pydeezer import Deezer
import os

from pydeezer.constants import track_formats


def download_track(track_id, track_directory, arl):
    deezer = Deezer(arl=arl)
    track = deezer.get_track(track_id)
    download_path = os.path.join(track_directory, str(track_id))
    if not os.path.exists(track_directory):
        os.makedirs(track_directory)
    # TODO check if file already exists and return 
    try:
        track["download"](download_path, quality=track_formats.MP3_320, filename=str(track_id))
    except Exception:
        pass
    return os.path.join(download_path, str(track_id) + ".mp3")

# def download_playlist(playlist_search_result, arl):
#     return
def get_track_id(track_id, arl):
    deezer = Deezer(arl=arl)
    return deezer.get_track(track_id)

def search_first_track(track_name, arl):
    deezer = Deezer(arl=arl)
    result = deezer.search_tracks(query=track_name, limit=1)
    if result:
        return result[0]

def search_first_playlist(playlist_name, arl):
    deezer = Deezer(arl=arl)
    result = deezer.search_playlists(query=playlist_name, limit=1)
    if result:
        return result[0]

def get_user_info(arl):
    deezer = Deezer(arl=arl)
    return deezer.user["name"]
