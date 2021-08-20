import os
import logging
import requests
from urllib.parse import urlparse
from pyrogram import Client, filters
from pyrogram.types.messages_and_media import Photo, Animation
from pyrogram.errors.exceptions.forbidden_403 import Forbidden
from .. import config, help_dict, log_errors, session, slave, public_log_errors

help_text = ''

def _generate(i):
    @Client.on_message(~filters.forwarded & ~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(i, prefixes=config['config']['prefixes']))
    @log_errors
    @public_log_errors
    async def func(client, message):
        bot = await slave.get_me()
        results = await client.get_inline_bot_results(bot.username or bot.id, i)
        result = results.results[0]
        to_reply = message
        if not getattr(message.reply_to_message, 'empty', True):
            to_reply = message.reply_to_message
        try:
            animation = os.path.splitext(urlparse(result.send_message.message).path)[1] == '.gif'
            if animation:
                await to_reply.reply_animation(result.send_message.message, caption=result.send_message.message)
            else:
                await to_reply.reply_photo(result.send_message.message, caption=result.send_message.message)
        except Forbidden:
            await to_reply.reply_text(result.send_message.message)
    return func

try:
    resp = requests.get('https://nekos.life/api/v2/endpoints')
    json = resp.json()
except BaseException:
    logging.exception('Cannot connect to nekos.life')
else:
    for i in json:
        _, i = i.split(' ', 1)
        i = i.strip()
        if i.startswith('/api/v2/img/<\''):
            for i in os.path.basename(i)[1:-1].split(', '):
                i = i[1:-1]
                if 'v3' in i:
                    continue
                func = _generate(i)
                globals()[i] = func
                locals()[i] = func
                func = None
                help_text += '{prefix}' + i.lower() + f' - Gets a {"gif" if "gif" in i else "picture"} of {i.lower()}\n'
            break
    help_dict['nekos'] = ('Nekos.life', help_text + '\nCan also be activated inline with: @{bot} <i>&lt;command without prefix&gt;</i>')
