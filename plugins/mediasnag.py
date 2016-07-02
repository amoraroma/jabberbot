import os
import glob
import shutil
import urllib.parse as up
import youtube_dl

from telepot import glance
from soundscrape import soundscrape

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
            'outtmpl': 'data/mediasnag/youtube/%(title)s-%(id)s.%(ext)s',
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

        # Add 'artist_url' before downloading
        self._ss_opts = {
            'open': False,
            'group': False,
            'mixcloud': False,
            'likes': False,
            'keep': False,
            'hive': False,
            'audiomack': False,
            'bandcamp': False,
            'num_tracks': 1,
            'track': '',
            'downloadable': False,
            'folders': 'data/mediasnag/soundcloud/'
        }

        if not os.path.isdir('data/mediasnag/'):
            os.mkdir('data/mediasnag/')
        if not os.path.isdir('data/mediasnag/youtube/'):
            os.mkdir('data/mediasnag/youtube/')
        if not os.path.isdir('data/mediasnag/soundcloud/'):
            os.mkdir('data/mediasnag/soundcloud/')

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

        if url_p.netloc in ['youtube.com', 'youtu.be']:
            v_id = up.parse_qs(url_p.query)['v'][0]
            found = glob.glob('data/mediasnag/*-{}.mp3'.format(v_id))

            if len(found) == 0:
                bot._dbg('Snagging audio from {}...'.format(v_id), tag='PLUGIN', level=2)
                await bot.sendMessage(chat_id, 'One sec, I gotta snag it first.', reply_to_message_id=m_id)

                with youtube_dl.YoutubeDL(self._ydl_opts) as ydl:
                    ydl.download([url])

                fn = glob.glob('data/mediasnag/*-{}.mp3'.format(v_id))[0]
            else:
                bot._dbg('Sending cached audio for {}...'.format(v_id), tag='PLUGIN', level=2)
                await bot.sendMessage(chat_id, 'Already snagged that one. Lemme send it.', reply_to_message_id=m_id)
                fn = found[0]

            title = os.path.basename(fn).replace('-{}.mp3'.format(v_id), '')

            self._dbg('Sending audio...', tag='PLUGIN', level=2)
            await bot.sendChatAction(chat_id, 'upload_audio')
            with open(fn, 'rb') as f:
                await bot.sendAudio(chat_id, f, title=title, reply_to_message_id=m_id)
        elif url_p.netloc == 'soundcloud.com':
            ss_opts = self._ss_opts.copy()
            ss_opts['artist_url'] = url
            a_id = url_p.path.split('/')[1]
            t_id = url_p.path.split('/')[-1]
            fbase = t_id.replace('-', ' - ').title()
            fname = 'data/mediasnag/soundcloud/{0}/{0} - {1}.mp3'.format(a_id, fbase)

            if os.path.isfile(fname):
                bot._dbg()
                bot._dbg('Sending cached audio for {}/{}...'.format(a_id, t_id), tag='PLUGIN', level=2)
                await bot.sendMessage(chat_id, 'Already snagged that one. Lemme send it.', reply_to_message_id=m_id)
                await bot.sendChatAction(chat_id, 'upload_audio')
                with open(fname, 'rb') as f:
                    await bot.sendAudio(chat_id, f, title=fbase, reply_to_message_id=m_id)
            else:
                bot._dbg('Snagging audio from {}/{}...'.format(a_id, t_id), tag='PLUGIN', level=2)
                await bot.sendMessage(chat_id, 'One sec, I gotta snag it first.', reply_to_message_id=m_id)
                soundscrape.process_soundcloud(ss_opts)
                shutil.move(a_id, 'data/mediasnag/soundcloud/')
                await bot.sendChatAction(chat_id, 'upload_audio')
                with open(fname, 'rb') as f:
                    await bot.sendAudio(chat_id, f, title=fbase, reply_to_message_id=m_id)
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