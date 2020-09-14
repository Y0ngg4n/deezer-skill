from mycroft import MycroftSkill, intent_file_handler


class Deezer(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('deezer.intent')
    def handle_deezer(self, message):
        artist = ''
        tracks = ''

        self.speak_dialog('deezer', data={
            'tracks': tracks,
            'artist': artist
        })


def create_skill():
    return Deezer()

