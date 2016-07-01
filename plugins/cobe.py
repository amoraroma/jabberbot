import os
from telepot import glance
from cobe.brain import Brain


__author__ = 'sli'
__version__ = '0.1'
__doc__ = '''Uses Cobe to learn grammar and generate responses. Unless silenced, it will respond to messages automatically.
Commands:
  * /ask <text> - Get a reply. (Example: /ask tell me about clouds)'''


class CobePlugin(object):
    def __init__(self):
        if not os.path.isfile('data/jabberbot.brain'):
            Brain.init('data/jabberbot.brain')

        self.brain = Brain('data/jabberbot.brain')
        self.silent = None

    async def run(self, msg, bot):
        # Don't learn URLs.
        if 'entities' in msg:
            for e in msg['entities']:
                if e['type'] == 'url':
                    return

        if not self.silent:
            if 'cobe' in bot.config:
                ccfg = bot.config.get('cobe', {})
                self.silent = ccfg.get('silent', True)

        self.brain.learn(msg['text'])

        if not self.silent:
            content_type, chat_type, chat_id = glance(msg)
            m_id = msg['message_id']
            reply = self.brain.reply(msg['text'])
            await bot.sendMessage(chat_id, reply, reply_to_message_id=m_id)

    async def ask(self, msg, bot):
        content_type, chat_type, chat_id = glance(msg)
        m_id = msg['message_id']
        text = msg['text'].split(' ', 1)[1]
        if len(text) > 0:
            self.brain.learn(text)
            reply = self.brain.reply(text)
        else:
            reply = 'You didn\'t say anything.'

        await bot.sendMessage(chat_id, reply, reply_to_message_id=m_id)

    def get_reply(self, incoming_msg, bot):
        self.brain.learn(incoming_msg)
        reply = self.brain.reply(incoming_msg)
        return reply

p = CobePlugin()

exports = {
    'self': p,
    'text': p.run,
    '/ask': p.ask
}
