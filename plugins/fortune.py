import os
import glob
import random
import platform
import subprocess

from telepot import glance

__author__ = 'sli'
__version__ = '0.2.1'
__doc__ = '''Tells you your fortune. Available sources are: {}

Commands:
  * /fortune [source] (Example: /fortune {}; /fortune)'''


class FortunePlugin(object):
    def __init__(self) -> None:
        self.fortunes = {}
        fortune_files = glob.glob('data/fortunes/*')
        for fortune_file in fortune_files:
            source_name = os.path.basename(fortune_file)
            with open(fortune_file, 'r') as f:
                fortunes = f.read().split('\n%\n')
                self.fortunes[source_name] = list(filter(None, fortunes))
        self._sources = list(self.fortunes.keys())

    def setup(self, bot) -> None:
        global __doc__

        if not 'fortune' in bot.config:
            bot.config['fortune'] = {}

    async def run(self, msg: dict, bot) -> None:
        content_type, chat_type, chat_id = glance(msg)
        m_id = msg['message_id']
        args = msg['text'].split(' ')[1:]
        source = None
        if len(args) > 0 and args[0] != '-c':
            if args[0] in self.fortunes:
                source = args[0]
                reply = random.choice(self.fortunes[source])
            else:
                reply = 'Possible fortune sources:\n'
                reply += ', '.join(self.fortunes.keys())
        else:
            source = random.choice(list(self.fortunes.keys()))
            reply = random.choice(self.fortunes[source])

        if source == 'cookie':
            lucky = [str(random.randint(1, 70)) for i in range(5)]
            lucky.append(str(random.randint(1, 27)))
            reply += '\n\nLucky numbers: {}'.format(', '.join(lucky))

        await bot.sendMessage(chat_id, reply, reply_to_message_id=m_id)


p = FortunePlugin()
__doc__ = __doc__.format(', '.join(p._sources), random.choice(p._sources))

exports = {
    'self': p,
    '/fortune': p.run
}
