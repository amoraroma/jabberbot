import time
import random
import asyncio
import telepot
import importlib
import telepot.async


__version__ = '0.2'
__prompt__ = '::'
__banner__ = 'Jabberbot'

_started = time.time()

DEBUG = 3
_longest_tag = 6

def _dbg(msg, tag='INFO', level=0):
    global DEBUG, _longest_tag
    
    if level <= DEBUG:
        if msg == '':
            tag = '\\\\/'
        if len(tag) > _longest_tag:
            _longest_tag = len(tag)
        tag = '[{}]'.format(tag).rjust(_longest_tag + 2)
        print('[{}] {} {} {}'.format(time.asctime(), tag,
                                     __prompt__, msg))


class JabberBot(telepot.async.Bot):
    def __init__(self, *args, **kwargs):
        self.config_file = kwargs['config']
        del kwargs['config']

        super(JabberBot, self).__init__(*args, **kwargs)
        self._dbg = _dbg
        self._answerer = telepot.async.helper.Answerer(self)
        self.load()

    async def on_chat_message(self, msg):
        global _started 
        content_type, chat_type, chat_id = telepot.glance(msg)

        if content_type == 'text':
            # chat = msg['chat']['id']
            # user = msg['from']['username']
            content = msg['text']

            if content[0] == '/':
                command = content.split(' ')[0].lower()

                # If the command is targeted, only run commands
                # targeted at me.
                if '@' in command:
                    command, atuser = command.split('@')
                    if not atuser == self.config['username'].lower():
                        return

                if command == '/reload' and \
                   msg['from']['id'] == self.config['admin']:
                    del self.plugins
                    _dbg('', level=2)
                    self.load()
                    await self.sendMessage(chat_id, 'Jabberbot reloaded!')
                elif command == '/quit' and \
                     msg['from']['id'] == self.config['admin'] and \
                     (time.time() - _started) > 20:
                    await self.sendMessage(chat_id, '-- jabberbot.')
                    loop.run_until_complete(asyncio.sleep(0))
                    sys.exit(0)
                elif command in ['/help', '/start']:
                    m_id = msg['message_id']
                    args = content.split(' ')[1:]
                    if len(args) > 0:
                        if args[0] in self.plugins:
                            reply = self.plugins[args[0]].__doc__
                            await self.sendMessage(chat_id, reply, reply_to_message_id=m_id)
                    else:
                        pl = list(self.plugins.keys())
                        pl.sort()
                        plugin_list = ', '.join(pl)
                        reply = 'Available plugins: {}\n'.format(', '.join(pl))
                        reply += 'Try: /help {}, or any other plugin.'.format(random.choice(pl))
                        await self.sendMessage(chat_id, reply, reply_to_message_id=m_id)
                else:
                    await self._dispatch(command, msg)
            else:
                await self._dispatch('text', msg)
        else:
            await self._dispatch(content_type, msg)

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

    def load(self):
        global DEBUG, __prompt__

        with open(self.config_file, 'r') as f:
            self.config = json.load(f)

        if 'debug' in self.config:
            DEBUG = int(self.config['debug'])

        if 'prompt' in self.config:
            __prompt__ = self.config['prompt']

        self.plugins = {}
        for plugin in self.config['plugins']:
            path = 'plugins.{}'.format(plugin)
            self.plugins[plugin] = importlib.import_module(path)

            tmpl = 'Loaded plugin: {} v{} ({})'
            tmpl_vars = (plugin,
                         self.plugins[plugin].__version__,
                         self.plugins[plugin].__author__)
            _dbg(tmpl.format(*tmpl_vars), 'SYS', level=1)

        _dbg('', level=2)
        for plugin in self.config['plugins']:
            self.plugins[plugin].exports['self'].setup(self)
        _dbg('', level=2)

    async def _dispatch(self, command, msg):
        for plugin in self.plugins:
            if command in self.plugins[plugin].exports:
                _dbg('Invoking {} for command {}.'.format(plugin, command),
                     tag='PLUGIN', level=4)
                func = self.plugins[plugin].exports[command]
                await func(msg, self)


if __name__ == '__main__':
    import json

    with open('token') as f:
        TOKEN = f.read().rstrip()

    bot = JabberBot(TOKEN, config='jabberbot.cfg')

    loop = asyncio.get_event_loop()
    loop.create_task(bot.message_loop())

    _dbg('{} v{} ready.'.format(__banner__, __version__))

    good = False
    try:
        loop.run_forever()
    except (KeyboardInterrupt, SystemExit):
        good = True
    except:
        good = False

    if good:
        _dbg('Goodbye!', tag='GOOD')
    else:
        _dbg('Ouch!', tag='ERROR')

