import os
import time
import requests
import subprocess
import speech_recognition as sr
from telepot import glance
from gtts import gTTS
from pydub import AudioSegment

__author__ = 'sli'
__version__ = '0.1.1'
__doc__ = '''A talkative feature. Reacts automatically to voice messages.'''


class TalkBackPlugin(object):
    def __init__(self) -> None:
        if not os.path.isdir('data/talkback'):
            os.mkdir('data/talkback')
        self._recog = sr.Recognizer()

    def setup(self, bot) -> None:
        self._dbg = bot._dbg

    async def run(self, msg: dict, bot) -> None:
        if not msg['chat']['type'] == 'private':
            # Only work with private chats to keep people sane
            return
        content_type, chat_type, chat_id = glance(msg)
        m_id = msg['message_id']
        file_id = msg['voice']['file_id']
        file_info = await bot.getFile(file_id)
        path = file_info['file_path']
        audio_url = 'https://api.telegram.org/file/bot{}/{}'
        audio_url = audio_url.format(bot._token, path)
        message_audio = 'data/talkback/{}.ogg'.format(file_id)

        with open(message_audio, 'wb') as f:
            r = requests.get(audio_url)
            f.write(r.content)

        of = message_audio.replace('.ogg', '.flac')
        voice = AudioSegment.from_ogg(message_audio)
        voice.export(of, format='flac')
        os.remove(message_audio)

        with sr.AudioFile(of) as source:
            audio = self._recog.record(source)

        incoming_message = self._recog.recognize_google(audio)
        os.remove(of)

        self._dbg('{} said: {}'.format(msg['from']['first_name'],
                                       incoming_message),
                  tag='PLUGIN', level=4)

        get_reply = bot.plugins['cobe'].exports['self'].get_reply
        reply_text = '{}'.format(get_reply(incoming_message))
        reply_audio = gTTS(text=reply_text, lang='en')
        audio_file = 'data/talkback/{}-reply.ogg'.format(time.time())
        reply_audio.save(audio_file)

        with open(audio_file, 'rb') as f:
            await bot.sendVoice(chat_id, f, reply_to_message_id=m_id)

        os.remove(audio_file)

p = TalkBackPlugin()

exports = {
    'self': p,
    'voice': p.run
}
