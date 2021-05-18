import os
import time
import html
import asyncio
import datetime
import tempfile
from decimal import Decimal
from urllib.parse import quote as urlencode
from pyrogram import Client, filters
from pyrogram.types import Sticker
from .. import config, help_dict, log_errors, session, progress_callback, public_log_errors

@Client.on_message(~filters.forwarded & ~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(['trace', 'tracemoe', 'whatanime', 'wa', 'wait'], prefixes=config['config']['prefixes']))
@log_errors
@public_log_errors
async def whatanime(client, message):
    media = message.photo or message.animation or message.video or message.sticker or message.document
    if not media:
        reply = message.reply_to_message
        if not getattr(reply, 'empty', True):
            media = reply.photo or reply.animation or reply.video or reply.sticker or reply.document
    if not media:
        await message.reply_text('Photo or GIF or Video or Sticker required')
        return
    if isinstance(media, Sticker) and media.is_animated:
        await message.reply_text('No animated stickers')
        return
    with tempfile.TemporaryDirectory() as tempdir:
        reply = await message.reply_text('Downloading...')
        path = await client.download_media(media, file_name=os.path.join(tempdir, '0'), progress=progress_callback, progress_args=(reply, 'Downloading...', False))
        new_path = os.path.join(tempdir, '1.png')
        proc = await asyncio.create_subprocess_exec('ffmpeg', '-i', path, '-frames:v', '1', new_path)
        await proc.communicate()
        await reply.edit_text('Uploading...')
        with open(new_path, 'rb') as file:
            async with session.post('https://api.trace.moe/search?cutBorders&anilistInfo', data={'image': file}) as resp:
                json = await resp.json(content_type=None)
    if json.get('error'):
        await reply.edit_text(json['error'], parse_mode=None)
    else:
        try:
            match = json['result'][0]
        except IndexError:
            await reply.edit_text('No match')
        else:
            nsfw = match['anilist']['isAdult']
            title_native = match['anilist']['title']['native']
            title_english = match['anilist']['title']['english']
            title_romaji = match['anilist']['title']['romaji']
            synonyms = ', '.join(match['anilist']['synonyms'])
            anilist_id = match['anilist']['id']
            episode = match['episode']
            similarity = match['similarity']
            from_time = str(datetime.timedelta(seconds=match['from'])).split('.', 1)[0].rjust(8, '0')
            to_time = str(datetime.timedelta(seconds=match['to'])).split('.', 1)[0].rjust(8, '0')
            text = f'<a href="https://anilist.co/anime/{anilist_id}">{title_romaji}</a>'
            if title_english:
                text += f' ({title_english})'
            if title_native:
                text += f' ({title_native})'
            if synonyms:
                text += f'\n<b>Synonyms:</b> {synonyms}'
            text += f'\n<b>Similarity:</b> {(Decimal(similarity) * 100).quantize(Decimal(".01"))}%\n'
            if episode:
                text += f'<b>Episode:</b> {episode}\n'
            if nsfw:
                text += '<b>Hentai/NSFW:</b> Yes'
            async def _send_preview():
                with tempfile.NamedTemporaryFile() as file:
                    async with session.get(match['video']) as resp:
                        while True:
                            chunk = await resp.content.read(4096)
                            if not chunk:
                                break
                            file.write(chunk)
                    file.seek(0)
                    try:
                        await reply.reply_video(file.name, caption=f'{from_time} - {to_time}')
                    except BaseException:
                        await reply.reply_text('Cannot send preview :/')
            await asyncio.gather(reply.edit_text(text, disable_web_page_preview=True), _send_preview())

help_dict['whatanime'] = ('WhatAnime',
'''{prefix}whatanime <i>(as caption of Photo/GIF/Video/Sticker or reply)</i> - Reverse searches anime, thanks to trace.moe
Aliases: {prefix}trace, {prefix}tracemoe, {prefix}wa, {prefix}wait''')
