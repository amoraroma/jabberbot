import sys
import asyncio
import telepot
import telepot.async
import speech_recognition as sr

from cobe.brain import Brain
from gtts import gTTS


class JabberBot(telepot.async.Bot):
    def __init__(self, *args, **kwargs):
        super(JabberBot, self).__init__(*args, **kwargs)
        self._answerer = telepot.async.helper.Answerer(self)
        self.brain = Brain('jabberbot.brain')
        self.recog = sr.Recognizer()

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        print(msg)
        # with sr.AudioFile(message_audio) as source:
        #     audio = r.record(source)
        # incoming_message = r.recognize_google(audio)
        # b.learn(incoming_message)
        # b.reply(incoming_message)
        # reply_audio = gTTS(text=reply_text, lang='en')
        print('Chat Message:', content_type, chat_type, chat_id)

    def on_callback_query(self, msg):
        message = telepot.glance(msg, flavor='callback_query')
        query_id, from_id, query_data = message
        print('Callback Query:', query_id, from_id, query_data)

    def on_inline_query(self, msg):
        message = telepot.glance(msg, flavor='inline_query')
        query_id, from_id, query_string = message
        print('Inline Query:', query_id, from_id, query_string)

        def compute_answer():
            articles = [{'type': 'article',
                         'id': 'abc',
                         'title': query_string,
                         'message_text': query_string}]

            return articles

        self._answerer.answer(msg, compute_answer)

    def on_chosen_inline_result(self, msg):
        message = telepot.glance(msg, flavor='chosen_inline_result')
        result_id, from_id, query_string = message
        print('Chosen Inline Result:', result_id, from_id, query_string)


if __name__ == '__main__':
    with open('token') as f:
        TOKEN = f.read().rstrip()

    bot = JabberBot(TOKEN)

    loop = asyncio.get_event_loop()
    loop.create_task(bot.message_loop())

    print('Listening (for real) ...')
    loop.run_forever()
