import dice
from telepot import glance


class DicePlugin(object):
    def __init__(self):
        pass

    async def run(self, msg, tele):
        content_type, chat_type, chat_id = glance(msg)
        m_id = msg['message_id']
        roll_cmd = msg['text'].split(' ')[1]
        try:
            roll = dice.roll(roll_cmd)
        except:
            return

        if len(roll) > 100:
            reply = 'Come, now. That\'s a silly number of rolls.'
        else:
            rolls = ', '.join([str(r) for r in roll])
            total = str(sum(roll))
            reply = 'Your rolls: {}\nTotal: {}'.format(rolls, total)

        await tele.sendMessage(chat_id, reply, reply_to_message_id=m_id)


p = DicePlugin()

exports = {
    'self': p,
    '/roll': p.run
}
