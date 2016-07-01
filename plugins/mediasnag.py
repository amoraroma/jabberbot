import os
import glob
import urllib.parse as up
import youtube_dl

from telepot import glance

__author__ = 'sli'
__version__ = '0.1'
__doc__ = '''Downloads MP3s from YouTube.

Commands:
  * /snag <url>'''


class QuietLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print('YDL Error: {}'.format(msg))


class MediaSnagPlugin(object):
    def __init__(self):
        self._ydl_opts = {
            'outtmpl': 'data/mediasnag/%(title)s-%(id)s.%(ext)s',
            'noplaylist': True,
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'logger': QuietLogger(),
            'progress_hooks': [self._progress]
        }

    def setup(self, bot):
        self._dbg = bot._dbg


    async def run(self, msg, bot):
        content_type, chat_type, chat_id = glance(msg)
        m_id = msg['message_id']
        args = msg['text'].split(' ')[1:]
        if len(args) < 1:
            # reply = "You must specify a YouTube or SoundCloud URL."
            reply = "You must specify a URL."
            await bot.sendMessage(chat_id, reply, reply_to_message_id=m_id)
            return

        url = args[0].replace('www.', '')
        url_p = up.urlparse(url)

        if not os.path.isdir('data/mediasnag'):
            os.mkdir('data/mediasnag')

        if url_p.netloc == 'youtube.com':
            v_id = up.parse_qs(url_p.query)['v'][0]

            found = glob.glob('data/mediasnag/*-{}.mp3'.format(v_id))
            if len(found) == 0:
                await bot.sendAudio(chat_id, 'Give me a moment, I need to download it first.', reply_to_message_id=m_id)
                with youtube_dl.YoutubeDL(self._ydl_opts) as ydl:
                    bot._dbg('Snagging audio from {}...'.format(v_id), tag='PLUGIN')
                    ydl.download([url])
                fn = glob.glob('data/mediasnag/*-{}.mp3'.format(v_id))[0]
            else:
                fn = found[0]

            title = os.path.basename(fn).replace('-{}.mp3'.format(v_id), '')

            self._dbg('Sending audio...', tag='PLUGIN')
            await bot.sendChatAction(chat_id, 'upload_audio')
            with open(fn, 'rb') as f:
                await bot.sendAudio(chat_id, f, title=title, reply_to_message_id=m_id)
        # elif url_p.netloc == 'soundcloud.com':
        #     pass
        else:
            # reply = "You must specify a YouTube or SoundCloud URL."
            reply = "You must specify a YouTube URL."
            await bot.sendMessage(chat_id, reply, reply_to_message_id=m_id)

    def _progress(self, d):
        self._dbg('YDL Status: {}'.format(d['status']), tag='PLUGIN', level=3)
        if d['status'] != 'downloading':
            self._dbg('YDL Status: {}'.format(d['status']), tag='PLUGIN', level=2)


p = MediaSnagPlugin()

exports = {
    'self': p,
    '/snag': p.run
}