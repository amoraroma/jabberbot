import dice


class DicePlugin(object):
    def __init__(self):
        pass

    async def run(self, msg, tele):
        content_type, chat_type, chat_id = glance(msg)
        try:
            roll = dice.roll(msg['text'])
        except:
            return

        roll_values = [random.randint(1, sides+1) for r in range(rolls)]
        reply = 'Your rolls: {}\nTotal: {}'.format(', '.join(roll),
                                                   sum(roll))
        await tele.sendMessage(chat_id, reply, reply_to_message_id=m_id)


p = DicePlugin()

exports = {
    'self': p,
    '/roll': p.run
}