import os
import json
import random
import atexit

from telepot import glance

__author__ = 'sli'
__version__ = '0.1'
__doc__ = '''Saves and recalls quotes from other users.

Commands:
  * /quote [first name] (Example: /quote sli; /quote)'''


class QuotePlugin(object) -> None:
    def __init__(self):
        if os.path.isfile('data/quote/quotes'):
            with open('data/quote/quotes', 'r') as f:
                self.quotes = json.load(f)
        else:
            self.quotes = []

    def setup(self, bot) -> None:
        pass

    async def recv_quote(self, msg, bot) -> None:
        if 'forward_from' in msg:
            content_type, chat_type, chat_id = glance(msg)

            for q in self.quotes:
                t = '\n'.join(q[2].split('\n')[:-1])
                if msg['text'] == t:
                    reply = 'I already know this quote.'
                    await bot.sendMessage(chat_id, reply)
                    return

            if msg['forward_from']['first_name'] == bot.config['username']:
                reply = 'You can\'t quote me, human.'
                await bot.sendMessage(chat_id, reply)
                return

            quote = [
                msg['forward_from']['first_name'],
                msg['from']['first_name'],
                msg['text']
            ]
            self.quotes.append(quote)
            self.flush()
            reply = 'Added quote from {}.'.format(msg['forward_from']['first_name'])
            await bot.sendMessage(chat_id, reply)

    async def send_quote(self, msg, bot) -> None:
        if len(self.quotes) > 0:
            content_type, chat_type, chat_id = glance(msg)
            m_id = msg['message_id']
            args = msg['text'].split(' ')[1:]
            if len(args) > 0:
                name = args[0]
                quotes = self.get_quotes_by(name)
                if len(quotes) == 0:
                    reply = 'Sorry, I didn\'t find any quotes from {}.'
                    await bot.sendMessage(chat_id, reply.format(name),
                                          reply_to_message_id=m_id)
                    return
                quote = random.choice(quotes)
            else:
                quote = random.choice(self.quotes)

            reply = '{2}\n--{0} (Added by {1})'.format(*quote)
            await bot.sendMessage(chat_id, reply,
                                   reply_to_message_id=m_id)


    def get_quotes_by(self, name) -> list:
        return [q for q in self.quotes if name.lower() in q[0].lower()]

    def flush(self) -> None:
        with open('data/quote/quotes', 'w') as f:
            json.dump(self.quotes, f, indent=2)


p = QuotePlugin()
atexit.register(p.flush)

exports = {
    'self': p,
    'text': p.recv_quote,
    '/quote': p.send_quote
}
