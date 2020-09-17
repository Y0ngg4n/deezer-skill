import enum
import json
import re
import requests
from mycroft import MycroftSkill, intent_handler
import threading
from enum import Enum

from mycroft.skills.common_play_skill import CommonPlaySkill, CPSMatchLevel
from mycroft.skills.audioservice import AudioService

from . import deezer_utils
import os
import shutil
import time
import multiprocessing


class Deezer(CommonPlaySkill):
    def __init__(self):
        super(Deezer, self).__init__()
        self.regexes = {}
        self.playlist_data = None
        self.playlist_playing_index = None
        self.playing_wait_thread = None
        self.playing_thread = None

    def initialize(self):
        super().initialize()
        self.audio_service = AudioService(self.bus)
        self.add_event('mycroft.audio.service.next', self.next_track)
        self.add_event('mycroft.audio.service.prev', self.prev_track)
        self.add_event('mycroft.audio.service.pause', self.pause)
        self.add_event('mycroft.audio.service.resume', self.resume)
        self.arl = self.settings.get('arl')
        # TODO directory should probably default to self.file_system.path
        # This is a unique directory for each Skill. 
        # There's also mycroft.util.get_cache_directory if you intend it to be temporary
        self.music_dir = self.settings.get('music_dir', self.file_system.path)
        self.track_directory = os.path.join(self.music_dir, "track")

    def CPS_match_query_phrase(self, phrase):
        self.log.info(f"Check Query Phrase: {phrase}")

        phrase, cps_match_level, data = self.specific_query(phrase=phrase)
        if cps_match_level is None:
            track = deezer_utils.search_first_track(track_name=phrase, arl=self.arl)
            if track is None:
                return None
            else:
                track_id = track.get('id')
                self.speak_dialog(key="track_found",
                                  data={'title_short': track["title_short"], 'artist': track['artist']['name']})
                download_path = deezer_utils.download_track(track_id=track_id,
                                                            track_directory=self.track_directory,
                                                            arl=self.arl)
                data = {
                    "type": 0,
                    "track": download_path,
                    "track_id": track_id
                }
                if 'deezer' in phrase:
                    cps_match_level = CPSMatchLevel.EXACT
                else:
                    cps_match_level = CPSMatchLevel.TITLE

        return phrase, cps_match_level, data

    """ This method responds wether the skill can play the input phrase.

        The method is invoked by the PlayBackControlSkill.

        Returns: tuple (matched phrase(str),
                        match level(CPSMatchLevel),
                        optional data(dict))
                 or None if no match was found.
    """

    def CPS_start(self, phrase, data):
        if self.playing_thread is not None:
            self.playing_thread.kill()
            self.playing_thread = None
        if self.playlist_data is not None:
            self.playlist_data = None
        if self.playlist_playing_index is not None:
            self.playlist_playing_index = None

        if data['type'] == 0:
            self.log.info("TrackType is Track")
            self.CPS_play(data['track'])
        elif data['type'] == 1:
            self.log.info("TrackType is Playlist")
            playlist = data['playlist']
            self.playlist_data = data
            playlist_search_results = data['playlist_search_results']
            track_directory = os.path.join(self.music_dir, str(playlist_search_results['id']))
            self.playing_thread = multiprocessing.Process(target=self.playing_playlist,
                                                          args=(playlist, track_directory, 0))
            self.playing_thread.start()
            self.playing_thread.join()
            shutil.rmtree(track_directory, ignore_errors=True)

    """ Starts playback.
    
        Called by the playback control skill to start playback if the
        skill is selected (has the best match level)
    """

    def specific_query(self, phrase):
        # Check if saved
        # match = re.match(self.translate_regex('saved_songs'), phrase)
        # if match and self.saved_tracks:
        #     return (1.0, {'data': None,
        #                   'type': 'saved_tracks'})

        # Check if playlist
        phrase = phrase.lower()
        match = re.match(self.translate_regex('playlist'), phrase)
        if match:
            playlist_search_results = deezer_utils.search_first_playlist(match.groupdict()['playlist'], self.arl)
            if playlist_search_results:
                tracklist = requests.get(playlist_search_results['tracklist']).json()
                try:
                    data = tracklist["data"]
                    next_tracklist_url = tracklist['next']
                    try:
                        while True:
                            next_tracklist = requests.get(next_tracklist_url).json()
                            data += next_tracklist['data']
                            next_tracklist_url = next_tracklist['next']
                            self.log.info(next_tracklist_url)
                    except KeyError as index:
                        pass
                except KeyError as dataError:
                    pass
                return_data = {
                    'type': 1,
                    'playlist': data,
                    'playlist_search_results': playlist_search_results
                }
                return phrase, CPSMatchLevel.TITLE, return_data
            else:
                return phrase, CPSMatchLevel.GENERIC, None
        # Check album
        # match = re.match(self.translate_regex('album'), phrase)
        # if match:
        #     album = match.groupdict()['album']
        #     return self.query_album(album)
        #
        # # Check artist
        # match = re.match(self.translate_regex('artist'), phrase)
        # if match:
        #     artist = match.groupdict()['artist']
        #     return self.query_artist(artist)
        # match = re.match(self.translate_regex('song'), phrase)
        # if match:
        #     song = match.groupdict()['track']
        #     return self.query_song(song)

        return phrase, None, None

    def playing_playlist(self, playlist, track_directory, start_index):
        for i in range(start_index, len(playlist)):
            try:
                self.playlist_playing_index = i
                track_id = playlist[i]['id']
                downloaded_track = deezer_utils.download_track(track_id=track_id,
                                                               track_directory=track_directory, arl=self.arl)

                self.log.info(str(downloaded_track))
                self.CPS_play(downloaded_track)
                self.log.info("Playing now ...")
                duration = playlist[i]['duration']
                time.sleep(duration)
                shutil.rmtree(downloaded_track, ignore_errors=True)
            except Exception as e:
                print(e)
                self.log.error(e)

    def next_track(self):
        print("Nächster Track")
        if self.playlist_data is not None:
            if self.playing_thread is not None:
                self.playing_thread.kill()
                self.playing_thread = None

            playlist_search_results = self.playlist_data['playlist_search_results']
            track_directory = os.path.join(self.music_dir, str(playlist_search_results['id']))
            self.playing_thread = multiprocessing.Process(target=self.playing_playlist,
                                                          args=(self.playlist_data['playlist'], track_directory,
                                                                self.playlist_playing_index + 1))
            self.playing_thread.start()
            self.playing_thread.join()
            shutil.rmtree(track_directory, ignore_errors=True)
        pass

    def prev_track(self):
        if self.playlist_data is not None:
            if self.playing_thread is not None:
                self.playing_thread.kill()
                self.playing_thread = None

            playlist_search_results = self.playlist_data['playlist_search_results']
            track_directory = os.path.join(self.music_dir, str(playlist_search_results['id']))
            if self.playlist_playing_index == 0:
                index = 0
            else:
                index = self.playlist_playing_index + 1
            self.playing_thread = multiprocessing.Process(target=self.playing_playlist,
                                                          args=(self.playlist_data['playlist'], track_directory,
                                                                index))
            self.playing_thread.start()
            self.playing_thread.join()
            shutil.rmtree(track_directory, ignore_errors=True)
        pass

    def pause(self):
        pass

    def resume(self):
        pass

    def translate_regex(self, regex):
        if regex not in self.regexes:
            path = self.find_resource(regex + '.regex')
            if path:
                with open(path) as f:
                    string = f.read().strip()
                self.regexes[regex] = string
        return self.regexes[regex]

    @intent_handler('user.intent')
    def speak_user_name(self, message):
        self.log.info("Username Intent")
        self.speak_dialog(key='user', data={'user_name': deezer_utils.get_user_info(arl=self.arl)})


def create_skill():
    return Deezer()
