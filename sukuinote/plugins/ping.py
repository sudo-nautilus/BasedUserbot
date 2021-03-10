import time
from pyrogram import Client, filters
from .. import config, help_dict, log_errors, public_log_errors, log_ring

strings = {
    'ping': 'Pong!',
    'pong': 'Ping!'
}

@Client.on_message(~filters.forwarded & ~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(['ping', 'pong'], prefixes=config['config']['prefixes']))
@log_errors
@public_log_errors
async def ping_pong(client, message):
    text = strings[message.command[0].lower()]
    start = time.time()
    reply = await message.reply_text(f'{text}\n<b>Log Ring:</b> {len(log_ring)}/{log_ring.maxlen}')
    end = time.time()
    await reply.edit_text(f'{text} <i>{round((end-start)*1000)}ms</i>\n<b>Log Ring:</b> {len(log_ring)}/{log_ring.maxlen}')

help_dict['ping'] = ('Ping',
'''{prefix}ping - Pong!
{prefix}pong - Ping!''')
