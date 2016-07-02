import os
import glob
import json
from telepot import glance
from cobe.brain import Brain


__author__ = 'sli'
__version__ = '0.1'
__doc__ = '''Uses Cobe to learn grammar and generate responses. Unless silenced, it will respond to messages automatically.

Commands:
  * /ask <text> - Get a reply. (Example: /ask tell me about clouds)'''


class CobePlugin(object):
    def __init__(self):
        if not os.path.isdir('data/cobe/'):
            os.mkdir('data/cobe/')
        if not os.path.isfile('data/cobe/jabberbot.brain'):
            Brain.init('data/cobe/jabberbot.brain')

        self.brain = Brain('data/cobe/jabberbot.brain')

        if not os.path.isfile('data/cobe/lusers'):
            with open('data/cobe/lusers', 'w') as f:
                f.write('{}')

        with open('data/cobe/lusers', 'r') as f:
            self.lusers = json.load(f)

    def setup(self, bot):
        if not 'cobe' in bot.config:
            bot.config['cobe'] = {}

        ccfg = bot.config['cobe']
        self.silent = ccfg.get('silent', True)

        self._dbg = bot._dbg

        if os.path.isfile('data/cobe/train.txt'):
            self._dbg('Training file found.' tag='PLUGIN')
            self.brain.start_batch_learning()
            with open('data/cobe/train.txt') as f:
                lines = f.read().split('\n')
                for line in lines:
                    self.brain.learn(line)
            self.brain.stop_batch_learning()
            t_files = glob.glob('data/cobe/train.txt.*')
            dst = 'data/cobe/train.txt.{}'.format(len(t_files))
            os.rename('data/cobe/train.txt', dst)
            self._dbg('Training complete. Training file moved to {}.'
                      .format(os.path.basename(dst)))

    async def run(self, msg, bot):
        # Don't learn URLs.
        if 'entities' in msg:
            for e in msg['entities']:
                if e['type'] == 'url':
                    return

        self.brain.learn(msg['text'])

        m_type = msg['chat']['type']
        u_id = 'id_' + str(msg['from']['id'])

        if (not self.silent or \
           (m_type == 'private' and self.lusers[u_id])) and
           'forward_from' not in msg:
            content_type, chat_type, chat_id = glance(msg)
            m_id = msg['message_id']
            reply = self.brain.reply(msg['text'])
            await bot.sendMessage(chat_id, reply)

    async def ask(self, msg, bot):
        content_type, chat_type, chat_id = glance(msg)
        m_id = msg['message_id']
        text = msg['text'].split(' ', 1)[1]
        if len(text) > 0:
            self.brain.learn(text)
            reply = self.brain.reply(text)
            await bot.sendMessage(chat_id, reply, reply_to_message_id=m_id)

    async def chat(self, msg, bot):
        content_type, chat_type, chat_id = glance(msg)
        command = msg['text'].split(' ', 1)[0]
        args = msg['text'].split(' ')[1:]
        u_id = 'id_' + str(msg['from']['id'])
        if len(args) > 0:
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

        print(self.lusers)
        self._flush()

    def get_reply(self, incoming_msg, bot):
        self.brain.learn(incoming_msg)
        reply = self.brain.reply(incoming_msg)
        return reply

    def _flush(self):
        with open('data/cobe/lusers', 'w') as f:
            json.dump(self.lusers, f, indent=2)

p = CobePlugin()

exports = {
    'self': p,
    'text': p.run,
    '/ask': p.ask,
    '/chat': p.chat
}
