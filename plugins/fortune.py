import os
import glob
import random

from telepot import glance


class FortunePlugin(object):
    def __init__(self):
        self.fortunes = {}
        fortune_files = glob.glob('data/fortunes/*')
        for fortune_file in fortune_files:
            source_name = os.path.basename(fortune_file)
            with open(fortune_file, 'r') as f:
                fortunes = f.read().split('\n%\n')
                self.fortunes[source_name] = list(filter(None, fortunes))

    async def run(self, msg, tele):
        content_type, chat_type, chat_id = glance(msg)
        m_id = msg['message_id']
        args = msg['text'].split(' ')[1:]
        if len(args) > 0:
            if args[0] in self.fortunes:
                source = args[0]
                reply = random.choice(self.fortunes[source])
            else:
                sources = ' '.join(self.fortunes.keys())
                reply = 'Possible fortune sources:\n'
                for s in sources:
                    reply += ' * {}'.format(s)
        else:
            source = random.choice(self.fortunes.keys())
            reply = random.choice(self.fortunes[source])
        await tele.sendMessage(chat_id, reply, reply_to_message_id=m_id)


p = FortunePlugin()

exports = {
    'self': p,
    '/fortune': p.run
}
