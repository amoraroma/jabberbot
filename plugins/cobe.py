import os
from telepot import glance
from cobe.brain import Brain


__author__ = 'sli'
__version__ = '0.1'
__doc__ = '''Uses Cobe to learn grammar and generate responses. Reacts automatically to chat messages.'''

class CobePlugin(object):
    def __init__(self):
        if not os.path.isfile('data/jabberbot.brain'):
            Brain.init('data/jabberbot.brain')

        self.brain = Brain('data/jabberbot.brain')

    async def run(self, msg, bot):
        content_type, chat_type, chat_id = glance(msg)
        # m_id = msg['message_id']
        self.brain.learn(msg['text'])
        # reply = self.brain.reply(msg['text'])
        # reply = 'Hello, plugins!'
        # await bot.sendMessage(chat_id, reply, reply_to_message_id=m_id)

    def get_reply(self, incoming_msg, bot):
        self.brain.learn(incoming_msg)
        reply = self.brain.reply(incoming_msg)
        return reply

p = CobePlugin()

exports = {
    'self': p,
    'text': p.run
}
