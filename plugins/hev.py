import os
import glob
import time
from pydub import AudioSegment


__author__ = 'sli'
__version__ = '0.1.0'
__doc__ = '''The voice of the HEV Suit.

Use {time} to insert the current time.
Commas and periods are recognized.

Extra words:
  * fuzz2 - Battery pickup double beep
  * mag_low - Low magazine warning beeps

Commands:
  * /hev <sentence>
  * /wordlist'''

num_words = ['zero', 'one', 'two', 'three', 'four', 'five',
             'six', 'seven', 'eight', 'nine', 'ten', 'eleven',
             'twelve', 'thirteen', 'fourteen', 'fifteen',
             'sixteen', 'seventeen', 'eighteen', 'nineteen',
             'twenty']
tens_words = ['zero', 'ten', 'twenty', 'thirty', 'fourty', 'fifty',
              'sixty', 'seventy', 'eighty', 'ninety']


class HEVPlugin(object):
    def __init__(self) -> None:
        if not os.path.isdir('data/hev/'):
            os.path.mkdir('data/hev/')
        if not os.path.isdir('data/hev/fvox/'):
            os.path.mkdir('data/hev/fvox/')
        if not os.path.isdir('data/hev/tmp/'):
            os.path.mkdir('data/hev/tmp/')
        raw_words = glob.glob('data/hev/fvox/*.wav')
        self.words = [f.replace('data/hev/fvox/', '') for f in raw_words]

    def setup(self, bot) -> None:
        self._dbg = bot._dbg

    async def run(self, msg: dict, bot) -> None:
        content_type, chat_type, chat_id = glance(msg)
        m_id = msg['message_id']
        sentence_audio = await HEVPlugin.say(msg['text'])

        self._dbg('saying: {}'.format(msg['text']),
                  tag='PLUGIN', level=4)

        with open(sentence_audio) as f:
            bot.sendVoice(chat_id, f, reply_to_message_id=m_id)

        os.delete(sentence_audio)

    async def wordlist(self, msg: dict, bot) -> None:
        content_type, chat_type, chat_id = glance(msg)
        m_id = msg['message_id']
        reply = 'Word list: {}'.format(','.join(self.wordlist))
        bot.sendMessage(chat_id, reply, reply_to_message_id=m_id)

    @staticmethod
    async def say(self, sentence):
        sayable = sentence.replace('.', ' _period')
                          .replace(',', ' _comma')
                          .replace('{time}', HEVPlugin.say_time())
        audio = pydub.AudioSegment.empty()
        for word in sayable:
            if not os.path.isfile(f):
                word = 'warning2'
            f = 'data/hev/fvox/{}.wav'.format(word)
            audio += AudioSegment.from_wav(f)
        out_filename = 'data/hev/outputs/{}.wav'.format(time.time())
        audio.export(out_filename, format='ogg')
        return out_filename

    @staticmethod
    def say_time(self):
        time_sentence = ['time_is_now']
        hour = int(time.strftime('%I'))
        minutes = time.strftime('%M')
        ampm = time.strftime('%p').lower()
        time_sentence.append(num_words[hour])

        minutes_i = int(minutes)
        if minutes_i > 10 and minutes_i < 20:
            time_sentence.append(num_words[minutes_i])
        else:
            tens = int(minutes[0])
            time_sentence.append(tens_words[tens])
            ones = int(minutes[1])
            if ones > 0:
                time_sentence.append(num_words[ones])
        time_sentence.append(ampm)
        return time_sentence

p = HEVPlugin()

exports = {
    'self': p,
    '/hev': p.run
    '/wordlist': p.wordlist
}