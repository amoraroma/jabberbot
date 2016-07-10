import random
from telepot import glance

__author__ = 'sli'
__version__ = '0.1.1'
__doc__ = '''Generates for you a new fantasy name.

Commands:
  * /name'''


class NamePlugin(object):
    def __init__(self) -> None:
        with open('data/name/nouns', 'r') as f:
            self._nouns = f.read().rstrip().split('\n')
        with open('data/name/adjectives', 'r') as f:
            self._adjectives = f.read().rstrip().split('\n')
        with open('data/name/groups', 'r') as f:
            self._groups = f.read().rstrip().split('\n')
        with open('data/name/name-pieces', 'r') as f:
            self._name_pieces = f.read().rstrip().split('\n')
        with open('data/name/titles', 'r') as f:
            self._titles = f.read().rstrip().split('\n')

        self._orders = ('first', 'second', 'third', 'fourth', 'fifth',
                        'sixth', 'seventh', 'eighth', 'last')

    def setup(self, bot) -> None:
        pass

    async def run(self, msg: dict, bot) -> None:
        content_type, chat_type, chat_id = glance(msg)
        m_id = msg['message_id']
        name_parts = self.generate_name()
        name = '{}, {} of the {} of the {} {}'.format(*name_parts[:-1])
        reply = 'You are now {}, {} of their name.'.format(name, name_parts[-1])
        await bot.sendMessage(chat_id, reply, reply_to_message_id=m_id)

    def generate_name(self) -> str:
        nameA = random.choice(self._name_pieces)
        nameB = nameA
        while nameA == nameB:
            nameB = random.choice(self._name_pieces)
        if nameA[-1] == nameB[0]:
            nameB = nameB[1:]
        name = nameA+nameB
        noun = random.choice(self._nouns)
        adj = random.choice(self._adjectives)
        grp = random.choice(self._groups)
        title = random.choice(self._titles)
        order = random.choice(self._orders)
        return (name.capitalize(), title, noun, adj, grp, order)

p = NamePlugin()

exports = {
    'self': p,
    '/name': p.run
}