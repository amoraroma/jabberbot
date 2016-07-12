import os
import glob
import json
import time
from telepot import glance
from cobe.brain import Brain


__author__ = 'sli'
__version__ = '0.1'
__doc__ = '''Uses Cobe to learn grammar and generate responses. Unless silenced, it will respond to messages automatically.

Commands:
  * /ask <text> - Get a reply. (Example: /ask tell me about clouds)
  * /? - Shortcut for /ask.'''


class CobePlugin(object):
    def __init__(self) -> None:
        if not os.path.isdir('data/cobe/'):
            os.mkdir('data/cobe/')
        if not os.path.isdir('data/cobe/voice/'):
            os.mkdir('data/cobe/voice/')
        if not os.path.isfile('data/cobe/lusers'):
            with open('data/cobe/lusers', 'w') as f:
                f.write('{}')
        if not os.path.isfile('data/cobe/vlusers'):
            with open('data/cobe/vlusers', 'w') as f:
                f.write('{}')

        with open('data/cobe/lusers', 'r') as f:
            self.lusers = json.load(f)
        with open('data/cobe/vlusers', 'r') as f:
            self.vlusers = json.load(f)

        if not os.path.isfile('data/cobe/jabberbot.brain'):
            Brain.init('data/cobe/jabberbot.brain')
        self.brain = Brain('data/cobe/jabberbot.brain')

    def setup(self, bot) -> None:
        self._dbg = bot._dbg

        if not 'cobe' in bot.config:
            bot.config['cobe'] = {}

        ccfg = bot.config['cobe']
        self.silent = ccfg.get('silent', True)

        if os.path.isfile('data/cobe/train.txt'):
            self._dbg('Training file found.', tag='PLUGIN', level=2)
            self.brain.start_batch_learning()
            with open('data/cobe/train.txt') as f:
                lines = f.read().split('\n')
                for line in lines:
                    line = line.lower().replace('"', '')
                    self.brain.learn(line)
            self.brain.stop_batch_learning()
            t_files = glob.glob('data/cobe/train.txt.*')
            dst = 'data/cobe/train.txt.{}'.format(len(t_files))
            os.rename('data/cobe/train.txt', dst)
            self._dbg('Training complete. Training file moved to {}.'
                      .format(os.path.basename(dst)), level=2)

    async def run(self, msg: dict, bot) -> None:
        # Don't learn URLs.
        if 'entities' in msg:
            for e in msg['entities']:
                if e['type'] == 'url':
                    return

        self.brain.learn(msg['text'].lower().replace('"', ''))

        m_type = msg['chat']['type']
        u_id = 'id_' + str(msg['from']['id'])

        if not u_id in self.lusers:
            self.lusers[u_id] = False
            self._flush()

        if (not self.silent or \
           (m_type == 'private' and self.lusers[u_id])) and \
           'forward_from' not in msg and \
           'reply_to_message' not in msg:
            content_type, chat_type, chat_id = glance(msg)
            m_id = msg['message_id']
            reply = self.brain.reply(msg['text'])
            # if m_type == 'private' and self.lusers[u_id] and self.vlusers[u_id]:
            #     audio_file = await self.get_reply_audio(reply)
            #     await bot.sendChatAction(chat_id, 'upload_audio')
            #     with open(audio_file, 'wb') as f:
            #         await bot.sendVoice(chat_id, f, reply_to_message_id=m_id)
            # else:
            await bot.sendMessage(chat_id, reply)

    async def ask(self, msg: dict, bot, ret: bool=False) -> None:
        content_type, chat_type, chat_id = glance(msg)
        m_id = msg['message_id']
        text = msg['text'].split(' ', 1)
        if len(text) > 1:
            text = text[1]
            self.brain.learn(text)
            reply = self.brain.reply(text)
            if ret:
                return reply
            await bot.sendMessage(chat_id, reply, reply_to_message_id=m_id)
        return None

    async def ask_and_say(self, msg: dict, bot) -> None:
        content_type, chat_type, chat_id = glance(msg)
        m_id = msg['message_id']
        reply = await self.ask(msg, bot, ret=True)
        if not reply:
            return

        audio_file = await self.get_reply_audio(reply)
        await bot.sendChatAction(chat_id, 'upload_audio')
        with open(audio_file, 'wb') as f:
            await bot.sendVoice(chat_id, f, reply_to_message_id=m_id)

    async def chat(self, msg: dict, bot) -> None:
        content_type, chat_type, chat_id = glance(msg)
        command = msg['text'].split(' ', 1)[0]
        args = msg['text'].split(' ')[1:]
        u_id = 'id_' + str(msg['from']['id'])
        if len(args) > 0:
            args[0] = args[0].lower()
            if args[0] == 'on':
                self.lusers[u_id] = True
                reply = 'Chat is: on'
                await bot.sendMessage(chat_id, reply)
            elif args[0] == 'off':
                self.lusers[u_id] = False
                reply = 'Chat is: off'
                await bot.sendMessage(chat_id, reply)
            else:
                reply = 'Eh? Are you turning chat on or off?'
                await bot.sendMessage(chat_id, reply)
        else:
            p = self.lusers.get(u_id, False)
            ch = 'on' if p else 'off'
            reply = 'Chat is: {}'.format(ch)
            await bot.sendMessage(chat_id, reply)

        self._flush()

    async def vchat(self, msg: dict, bot) -> None:
        content_type, chat_type, chat_id = glance(msg)
        command = msg['text'].split(' ', 1)[0]
        args = msg['text'].split(' ')[1:]
        u_id = 'id_' + str(msg['from']['id'])
        if len(args) > 0:
            args[0] = args[0].lower()
            if args[0] == 'on':
                self.vlusers[u_id] = True
                reply = 'VChat is: on'
                await bot.sendMessage(chat_id, reply)
            elif args[0] == 'off':
                self.vlusers[u_id] = False
                reply = 'VChat is: off'
                await bot.sendMessage(chat_id, reply)
            else:
                reply = 'Eh? Are you turning vchat on or off?'
                await bot.sendMessage(chat_id, reply)
        else:
            p = self.vlusers.get(u_id, False)
            ch = 'on' if p else 'off'
            reply = 'VChat is: {}'.format(ch)
            await bot.sendMessage(chat_id, reply)

        self._flush()

    def get_reply(self, incoming_msg: str) -> str:
        self.brain.learn(incoming_msg)
        reply = self.brain.reply(incoming_msg)
        return reply

    async def get_reply_audio(self, reply: str) -> str:
        reply_audio = gTTS(text=reply, lang='en')
        audio_file = 'data/cobe/voice/reply-{}.mp3'.format(time.time())
        reply_audio.save(audio_file)
        return audio_file

    def _flush(self) -> None:
        with open('data/cobe/lusers', 'w') as f:
            json.dump(self.lusers, f, indent=2)
        with open('data/cobe/vlusers', 'w') as f:
            json.dump(self.vlusers, f, indent=2)

p = CobePlugin()

exports = {
    'self': p,
    'text': p.run,
    '/ask': p.ask,
    '/?': p.ask,
    # '/!': p.ask_and_say,
    '/chat': p.chat,
    # '/vchat': p.vchat
}
