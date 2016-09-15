import asyncio
from message import Message


@asyncio.coroutine
def run(message, matches, chat_id, step):
    return [Message(chat_id).set_text(
        "Hi :-) \n*Bot Search Music!*\n✔Fast and accurate✔\n\n_/Music <Artist name>_\n*Creator* = @LullSky", parse_mode="markdown")]


plugin = {
    "name": "About",
    "desc": "Get Information About The Developer!",
    "usage": ["/about"],
    "run": run,
    "sudo": False,
    "patterns": ["^[/]start$"]
}
