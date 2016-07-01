import requests

__author__ = 'sli'
__version__ = '0.1'
__doc__ = '''Links the specified Github repository.
Commands:
  * /github <repo> (Example: /github sli/jabberbot)'''


class GithubPlugin(object):
    def __init__(self):
        pass

    def run(self, msg, bot):
        pass


p = GithubPlugin()

exports = {
    'self': p,
    '/github': p.run
}
