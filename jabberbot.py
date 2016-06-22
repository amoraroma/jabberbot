import os
import sys
import time
import subprocess
import telepot
import telepot.async
import requests
import speech_recognition as sr

from cobe.brain import Brain
from gtts import gTTS


class JabberBot(telepot.async.Bot):
    def __init__(self, *args, **kwargs):
        super(JabberBot, self).__init__(*args, **kwargs)
        self._answerer = telepot.async.helper.Answerer(self)
        self._message_with_inline_keyboard = None

    async def on_chat_message(self, msg):
        print(msg)
        content_type, chat_type, chat_id = telepot.glance(msg)
        print('Chat Message:', content_type, chat_type, chat_id)

        if content_type == 'voice':
            print('Voice file found, downloading...')#, end=' ')
            file_id = msg['voice']['file_id']

            # Download audio
            path = self.getFile(file_id)['file_path']
            audio_url = 'https://api.telegram.org/file/bot{}/{}'.format(self._token, path)
            message_audio = 'voice/{}.ogg'.format(file_id)

            with open(message_audio, 'wb') as f:
                r = requests.get(audio_url)
                f.write(r.content)

            # Convert to flac
            of = message_audio.replace('.ogg', '.aiff')
            subprocess.check_call(['ffmpeg', '-i', message_audio, of],
                                  stdout=open('stdout.log', 'w'),
                                  stderr=open('stderr.log', 'w'),
                                  close_fds=True)

            print('Recognizing...')#, end=' ')
            with sr.AudioFile(message_audio) as source:
                audio = r.record(source)
            incoming_message = r.recognize_google(audio)

            # print('Learning...')#, end=' ')
            # b.learn(incoming_message)

            # print('Replying...')#, end=' ')
            # b.reply(incoming_message)

            # print('Speaking...')#, end=' ')
            # reply_audio = gTTS(text=reply_text, lang='en')

            print('Sending...')#, end=' ')
            self._answerer.answer(msg, incoming_message)

            print('Done.')

    async def on_callback_query(self, msg):
        pass

    def on_inline_query(self, msg):
        pass

    def on_chosen_inline_result(self, msg):
        pass


if __name__ == '__main__':
    with open('token') as f:
        TOKEN = f.read().rstrip()

    bot = JabberBot(TOKEN)
    loop = asyncio.get_event_loop()

    loop.create_task(bot.message_loop())
    print('Listening ...')

    loop.run_forever()
