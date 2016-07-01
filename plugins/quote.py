import os
import json
import random
import atexit

from telepot import glance


class QuotePlugin(object):
    def __init__(self):
        if not os.path.isfile('data/quotes'):
            with open('data/quotes', 'w') as f:
                f.write('[]')

        with open('data/quotes', 'r') as f:
            self.quotes = json.load(f)

    async def run(self, msg, tele):
        content_type, chat_type, chat_id = glance(msg)
        if 'forward_from' in msg:
            # add quote
            reply_to = msg['forward_from']
            quote = [
                reply_to['from']['first_name'],
                msg['from']['first_name'],
                reply_to['text']
            ]
            self.quotes[chat_id].append(quote)
            self.flush()
        else:
            # send quote
            # command = msg['text'].split(' ')[0]
            args = msg['text'].split(' ')[1:]
            m_id = msg['message_id']

            if len(self.quotes) > 0:
                if len(args) > 0:
                    name = args[0]
                    quotes = self.get_quotes_by(name, chat_id)
                    quote = random.choice(quotes)
                else:
                    quote = random.choice(self.quotes)

                q_text = quote[2]
                q_sname = quote[0]
                q_aname = quote[1]
                reply = '{}\n'.format(q_text)
                reply += '--{} (Added by @{})'.format(q_sname, q_aname)
                await tele.sendMessage(chat_id, reply,
                                       reply_to_message_id=m_id)

    def get_quotes_by(self, name, chat_id):
        return [q for q in self.quotes[chat_id] if name in q[0]]

    def flush(self):
        with open('data/quotes', 'w') as f:
            json.dump(self.quotes, f, indent=2)


p = QuotePlugin()
atexit.register(p.flush)

exports = {
    'self': p,
    '/quote': p.run
}
