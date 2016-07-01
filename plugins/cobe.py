import os
from telepot import glance
from cobe.brain import Brain

class CobePlugin(object):
    def __init__(self):
        if not os.path.isfile('data/jabberbot.brain'):
            Brain.init('data/jabberbot.brain')

        self.brain = Brain('data/jabberbot.brain')

    async def run(self, msg, tele):
        content_type, chat_type, chat_id = glance(msg)
        m_id = msg['message_id']
        # self.brain.learn(msg['text'])
        # reply = self.brain.reply(msg['text'])
        reply = 'Hello, plugins!'
        await tele.sendMessage(chat_id, reply, reply_to_message_id=m_id)

    def get_reply(self, incoming_msg, tele):
        # self.brain.leanr(incoming_msg)
        # reply = self.brain.reply(incoming_msg)
        reply = 'Hello, plugin API!'
        return reply

p = CobePlugin()

exports = {
    'self': p,
    'text': p.run
}