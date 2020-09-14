from mycroft import MycroftSkill, intent_file_handler

from mycroft.skills.common_play_skill import CommonPlaySkill, CPSMatchLevel
import deezer_utils

class Deezer(CommonPlaySkill):
    def __init__(self):
        super(Deezer, self).__init__()


    def CPS_match_query_phrase(self, phrase):
        if 'deezer' in phrase:
            return phrase, CPSMatchLevel.GENERIC
        else:
            return None

        track_id = deezer_utils.search_first_track(phrase)
        self.log.info("Track ID:" + track_id)
        self.speak_dialog("deezer.dialog")
        if track_id is None:
            return None
        else:
            data = {
                "track": deezer_utils.track_directory.join(str(track_id)),
                "track_id": track_id
            }

            return (phrase, CPSMatchLevel.EXACT, data)
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
        self.audioservice(data['track'])
        """ Starts playback.

            Called by the playback control skill to start playback if the
            skill is selected (has the best match level)
        """
        pass

    @intent_handler(IntentBuilder('').require('Deezer').require('User'))
    def list_devices(self, message):
        """ List available devices. """
        self.speak_dialog('user.name', {'user_name': deezer_utils.get_user_info(deezer_utils.arl)})


def create_skill():
    return Deezer()

