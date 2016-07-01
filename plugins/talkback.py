import speech_recognition as sr
from gtts import gTTS


class TalkBackPlugin(object):
    def __init__(self):
        self._recog = sr.Recognizer()

    def run(self, msg, tele):
        file_id = msg['voice']['file_id']
        path = self.getFile(file_id)['file_path']
        audio_url = 'https://api.telegram.org/file/bot{}/{}'.format(self._token, path)
        message_audio = 'voice/{}.ogg'.format(file_id)

        with open(message_audio, 'wb') as f:
            r = requests.get(audio_url)
            f.write(r.content)

        of = message_audio.replace('.ogg', '.flac')
        subprocess.check_call(['ffmpeg', '-i', message_audio, of],
                               stdout=open('stdout.log', 'w'),
                               stderr=open('stderr.log', 'w'),
                               close_fds=True)

        with sr.AudioFile(message_audio) as source:
            audio = self._recog.record(source)

        incoming_message = self._recog.recognize_google(audio)

        get_reply = tele.plugins['cobe'].exports['self'].get_reply
        reply_text = '{}, {}'.format(msg['from']['first_name'],
                                     get_reply(incoming_message, tele))
        reply_audio = gTTS(text=reply_text, lang='en')
        audio_file = '{}-reply.ogg'.format(time.time())
        reply_audio.save(audio_file)

        with open(audio_file, 'wb') as f:
            tele.sendVoice(int(time.time()), f)

p = TalkBackPlugin()

exports = {
    'self': p
    'audio': p.run
}