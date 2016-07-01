import os
import glob
import random
import subprocess

from telepot import glance

__author__ = 'sli'
__version__ = '0.1'
__doc__ = '''Tells you your fortune. Available sources are: {}. This fortune might have super cow powers.

Commands:
  * /fortune [source] (Example: /fortune {}; /fortune)'''


class FortunePlugin(object):
    def __init__(self, enable_cow=False):
        self.fortunes = {}
        fortune_files = glob.glob('data/fortunes/*')
        for fortune_file in fortune_files:
            source_name = os.path.basename(fortune_file)
            with open(fortune_file, 'r') as f:
                fortunes = f.read().split('\n%\n')
                self.fortunes[source_name] = list(filter(None, fortunes))
        self._sources = list(self.fortunes.keys())

    def setup(self, bot):
        try: 
            cs_sub = subprocess.Popen(['cowsay', '-l'],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
            output, err = cs_sub.communicate()
            output = output.decode('utf-8').rstrip().split('\n')[1:]
            output = ' '.join(output)
            self._cowfigs = output.split(' ')

            if 'fortune' in bot.config:
                dcs = bot.config['fortune'].get('disabled-cows', [])
                for dc in dcs:
                    print('remove: {}'.format(dc))
                    self._cowfigs.remove(dc)
        except:
            self._cowfigs = []

    async def run(self, msg, bot):
        content_type, chat_type, chat_id = glance(msg)
        m_id = msg['message_id']
        args = msg['text'].split(' ')[1:]
        if len(args) > 0 and args[0] != '-c':
            if args[0] in self.fortunes:
                source = args[0]
                reply = random.choice(self.fortunes[source])
            else:
                sources = ' '.join(self.fortunes.keys())
                reply = 'Possible fortune sources:\n'
                for s in sources:
                    reply += ' * {}'.format(s)
        else:
            source = random.choice(list(self.fortunes.keys()))
            reply = random.choice(self.fortunes[source])

        lucky = [str(random.randint(1, 101)) for i in range(6)]
        reply += '\n\nLucky numbers: {}'.format(', '.join(lucky))

        if '-c' in args and len(self._cowfigs) > 0:
            fig = random.choice(self._cowfigs)
            cmd = ['cowsay', '-f', fig, reply]
            cs = subprocess.Popen(cmd, stdout=subprocess.PIPE)
            reply, e = cs.communicate()
            reply = '```{}``` (fig: {})'.format(reply.decode('utf-8'), fig)

        await bot.sendMessage(chat_id, reply, reply_to_message_id=m_id, parse_mode='Markdown')


p = FortunePlugin()
__doc__ = __doc__.format(', '.join(p._sources), random.choice(p._sources))

exports = {
    'self': p,
    '/fortune': p.run
}
