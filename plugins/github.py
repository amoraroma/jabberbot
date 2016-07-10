import github
from telepot import glance

__author__ = 'sli'
__version__ = '0.1'
__doc__ = '''Links the specified Github repository.

Commands:
  * /github <repo> (Example: /github sli/jabberbot)'''


class GithubPlugin(object):
    def __init__(self) -> None:
        self._github = github.Github()

    def setup(self, bot) -> None:
        pass

    async def run(self, msg: dict, bot) -> None:
        command = msg['text'].split(' ')[0]
        args = msg['text'].split(' ')[1:]
        if len(args) > 0:
            content_type, chat_type, chat_id = glance(msg)
            m_id = msg['message_id']
            repo = self._github.get_repo(args[0])
            try:
                reply = '{}'.format(repo.html_url)
                await bot.sendMessage(chat_id, reply, reply_to_message_id=m_id)
            except:
                reply = 'Repo {} not found.'.format(args[0])
                await bot.sendMessage(chat_id, reply, reply_to_message_id=m_id)
        else:
            reply = 'You must specify a Github repo.'
            await bot.sendMessage(chat_id, reply, reply_to_message_id=m_id)


p = GithubPlugin()

exports = {
    'self': p,
    '/github': p.run
}
