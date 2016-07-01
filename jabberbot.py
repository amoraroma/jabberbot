import sys
import time
import pprint
import asyncio
import telepot
import importlib
import telepot.async


DEBUG = False

def _dbg(msg, tag='INFO'):
    if DEBUG:
        print('''[{}] [{}] {}'''.format(time.asctime(), tag, msg))


class JabberBot(telepot.async.Bot):
    def __init__(self, *args, **kwargs):
        self.config = kwargs['config']
        del kwargs['config']

        super(JabberBot, self).__init__(*args, **kwargs)

        self._answerer = telepot.async.helper.Answerer(self)

        self.plugins = {}
        self._text_processors = []
        self._audio_processors = []
        for plugin in self.config['plugins']:
            path = 'plugins.{}'.format(plugin)
            self.plugins[plugin] = importlib.import_module(path)

            if 'text' in self.plugins[plugin].exports:
                self._text_processors.append(plugin)
            if 'audio' in self.plugins[plugin].exports:
                self._audio_processors.append(plugin)

            _dbg('Loaded plugin: {}'.format(plugin), 'SYS')

    async def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)

        if content_type == 'text':
            chat = msg['chat']['id']
            user = msg['from']['username']
            content = msg['text']

            if content[0] == '/':
                command = content.split(' ')[0].lower()
                await self._dispatch(command, msg)
            else:
                _dbg(msg)
                await self._dispatch('text', msg)
        elif content_type == 'voice':
            await self._dispatch('audio', msg)

    def on_callback_query(self, msg):
        # message = telepot.glance(msg, flavor='callback_query')
        # query_id, from_id, query_data = message
        # print('Callback Query:', query_id, from_id, query_data)
        pass

    def on_inline_query(self, msg):
        # message = telepot.glance(msg, flavor='inline_query')
        # query_id, from_id, query_string = message
        # print('Inline Query:', query_id, from_id, query_string)

        # def compute_answer():
        #     articles = [{'type': 'article',
        #                  'id': 'abc',
        #                  'title': query_string,
        #                  'message_text': query_string}]

        #     return articles

        # self._answerer.answer(msg, compute_answer)
        pass

    def on_chosen_inline_result(self, msg):
        # message = telepot.glance(msg, flavor='chosen_inline_result')
        # result_id, from_id, query_string = message
        # print('Chosen Inline Result:', result_id, from_id, query_string)
        pass

    async def _dispatch(self, command, msg):
        for plugin in self.plugins:
            if command in self.plugins[plugin].exports:
                _dbg('Invoking {} for command {}.'.format(plugin, command),
                     'PLUGIN')
                func = self.plugins[plugin].exports[command]
                await func(msg, self)


if __name__ == '__main__':
    import json

    with open('token') as f:
        TOKEN = f.read().rstrip()
    with open('jabberbot.cfg') as f:
        config = json.loads(f.read())

    if 'debug' in config:
        DEBUG = config['debug']

    bot = JabberBot(TOKEN, config=config)

    loop = asyncio.get_event_loop()
    loop.create_task(bot.message_loop())

    _dbg('Listening ...')

    loop.run_forever()
