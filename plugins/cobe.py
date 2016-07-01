from cobe.brain import Brain

class CobePlugin(object):
    def __init__(self):
        self.brain = Brain('jabberbot.brain')

    def run(self, msg, tele):
        self.brain.learn(msg['text'])
        reply = self.brain.reply(msg['text'])
        tele._answerer.answer(reply)

    def get_reply(self, incoming_msg, tele):
        self.brain.leanr(incoming_msg)
        reply = self.brain.reply(incoming_msg)
        return reply

p = CobePlugin()

exports = {
    'self': p,
    'text': p.run
}