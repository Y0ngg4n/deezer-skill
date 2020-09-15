from mycroft import MycroftSkill, intent_handler

from mycroft.skills.common_play_skill import CommonPlaySkill, CPSMatchLevel
from . import deezer_utils
import os


class Deezer(CommonPlaySkill):
    def __init__(self):
        super(Deezer, self).__init__()

    def initialize(self):
        self.track_directory = os.path.join(self.settings.get('music_dir'), "track")

    def CPS_match_query_phrase(self, phrase):
        self.log.info("Check Query Phrase")
        if 'deezer' in phrase:
            return phrase, CPSMatchLevel.GENERIC

        track = deezer_utils.search_first_track(track_name=phrase, arl=self.settings.get('arl'))
        if track is None:
            return None
        else:
            track_id = track["id"]
            self.speak_dialog(key="track_found",
                              data={'title_short': track["title_short"], 'artist': track['artist']['name']})
            download_path = deezer_utils.download_track(track_id=track_id,
                                                        track_directory=self.track_directory,
                                                        arl=self.settings.get('arl'))
            data = {
                "track": download_path,
                "track_id": track_id
            }

            return phrase, CPSMatchLevel.EXACT, data
        """ This method responds wether the skill can play the input phrase.

            The method is invoked by the PlayBackControlSkill.

            Returns: tuple (matched phrase(str),
                            match level(CPSMatchLevel),
                            optional data(dict))
                     or None if no match was found.
        """
        return None

    def CPS_start(self, phrase, data):
        self.log.info("Track: " + data['track'])
        self.CPS_play(data['track'])
        """ Starts playback.

            Called by the playback control skill to start playback if the
            skill is selected (has the best match level)
        """

    @intent_handler('user.intent')
    def speak_user_name(self, message):
        self.log.info("Username Intent")
        self.speak_dialog(key='user', data={'user_name': deezer_utils.get_user_info(arl=self.settings.get('arl'))})


def create_skill():
    return Deezer()
