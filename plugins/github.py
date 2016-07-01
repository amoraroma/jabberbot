import github

__author__ = 'sli'
__version__ = '0.1'
__doc__ = '''Links the specified Github repository.
Commands:
  * /github <repo> (Example: /github sli/jabberbot)'''


class GithubPlugin(object):
    def __init__(self):
        self._github = github.Github()

    def run(self, msg, bot):
        command = msg.split(' ')[0]
        args = msg.split(' ')[1:]
        if len(args) > 0:
            content_type, chat_type, chat_id = glance(msg)
            m_id = msg['message_id']
            repo = g.get_repo(args[0])
            try:
                reply = 'Repo: {}'.format(repo.html_url)
            except:
                reply = 'Repo {} not found.'.format(args[0])
            bot.sendMessage(chat_id, reply, reply_to_message_id=m_id)


p = GithubPlugin()

exports = {
    'self': p,
    '/github': p.run
}
