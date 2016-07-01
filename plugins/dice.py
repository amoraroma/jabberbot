import dice
from telepot import glance

__author__ = 'sli'
__version__ = '0.1'
__doc__ = '''Rolls dice. Any dice.
Commands:
  * /roll <dice> (Example: /roll 5d6)'''


class DicePlugin(object):
    def __init__(self):
        pass

    async def run(self, msg, bot):
        content_type, chat_type, chat_id = glance(msg)
        m_id = msg['message_id']
        roll_cmd = msg['text'].split(' ')[1]
        try:
            roll = dice.roll(roll_cmd)
        except:
            return

        if isinstance(roll, int):
            reply = 'Total: {}'.format(roll)
        elif len(roll) > 100:
            reply = 'Come, now. That\'s a silly number of rolls.'
        else:
            rolls = ', '.join([str(r) for r in roll])
            total = str(sum(roll))
            reply = 'Your rolls: {}\nTotal: {}'.format(rolls, total)

        await bot.sendMessage(chat_id, reply, reply_to_message_id=m_id)


p = DicePlugin()

exports = {
    'self': p,
    '/roll': p.run
}
