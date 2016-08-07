import os
import json
import time
import chalk
import click
import random
import asyncio
import telepot
import importlib
import telepot.async


__version__ = '0.2.1'
__prompt__ = '::'
__banner__ = 'Jabberbot'

# _started = time.time()

DEBUG = 3
_longest_tag = 6

def _dbg(msg: str, tag: str='INFO', level: int=0) -> None:
    global DEBUG, _longest_tag

    if level <= DEBUG:
        if tag == 'INFO':
            disp = chalk.blue
        elif tag == 'PLUGIN':
            disp = chalk.yellow
        elif tag in ['SYS', 'BOT', 'INFO']:
            disp = chalk.green
        elif tag == 'GOOD':
            disp = chalk.cyan
        elif tag == 'ERROR':
            disp = chalk.red
        else:
            disp = chalk.white
        if msg == '':
            tag = '\\\\/'
            disp = chalk.cyan
        if len(tag) > _longest_tag:
            _longest_tag = len(tag)
        tag = '[{}]'.format(tag).rjust(_longest_tag + 2)
        message = '[{}] {} {} {}'.format(time.asctime(), tag,
                                         __prompt__, msg)
        disp(message)


class JabberBot(telepot.async.Bot):
    def __init__(self, *args, **kwargs) -> None:
        self._token = args[0]

        self.config_file = kwargs['config']
        del kwargs['config']

        super(JabberBot, self).__init__(*args, **kwargs)

        if not os.path.isdir('data/'):
            os.path.mkdir('data/')

        self._dbg = _dbg
        self._answerer = telepot.async.helper.Answerer(self)
        self.load()

    async def on_chat_message(self, msg: dict) -> None:
        # global _started
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
                # elif command == '/quit' and \
                #      msg['from']['id'] == self.config['admin'] and \
                #      (time.time() - _started) > 20:
                #     await self.sendMessage(chat_id, '-- jabberbot.')
                #     loop.run_until_complete(asyncio.sleep(0))
                #     sys.exit(0)
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

    def load(self) -> None:
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

    async def _dispatch(self, command: str, msg: dict) -> None:
        for plugin in self.plugins:
            if command in self.plugins[plugin].exports:
                _dbg('Invoking {} for command {}.'.format(plugin, command),
                     tag='PLUGIN', level=4)
                func = self.plugins[plugin].exports[command]
                await func(msg, self)


@click.command()
@click.option('--config', '-c', default='jabberbot.cfg',
              help=('Configuration file for this instance. '
                    'Default: jabberbot.cfg'))
@click.option('--token', '-t', default=None,
              help=('File containing the API token for the bot. '
                    'Default: token'))
def jabberbot(config, token):
    with open(token) as f:
        TOKEN = f.read().rstrip()

    bot = JabberBot(TOKEN, config=config)

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

if __name__ == '__main__':
    jabberbot()
