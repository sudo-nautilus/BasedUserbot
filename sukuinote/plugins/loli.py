from pyrogram import Client, filters
from pyrogram.types.messages_and_media import Photo
from pyrogram.errors.exceptions.forbidden_403 import Forbidden
from .. import slave, config, help_dict, log_errors, public_log_errors

@Client.on_message(~filters.forwarded & ~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(['loli', 'sfwloli', 'sloli', 'nsfwloli', 'nloli'], prefixes=config['config']['prefixes']))
@log_errors
@public_log_errors
async def loli(client, message):
    bot = await slave.get_me()
    query = ' '.join(message.command)
    results = await client.get_inline_bot_results(bot.username or bot.id, query)
    result = results.results[0]
    to_reply = message
    if not getattr(message.reply_to_message, 'empty', True):
        to_reply = message.reply_to_message
    if result.type != 'photo':
        await to_reply.reply_text({'message': result.send_message.message, 'entities': result.send_message.entities}, parse_mode='through')
        return
    photo = Photo._parse(client, result.photo)
    try:
        await to_reply.reply_cached_media(photo.file_id, caption={'message': result.send_message.message, 'entities': result.send_message.entities}, parse_mode='through')
    except Forbidden:
        await to_reply.reply_text({'message': result.send_message.message, 'entities': result.send_message.entities}, parse_mode='through')

help_dict['loli'] = ('Loli',
'''{prefix}loli <i>[keywords]</i> - Gets a possibly nsfw image of a loli, thanks to lolicon.app
Can also be activated inline with: @{bot} loli <i>[keywords]</i>

{prefix}sfwloli <i>[keywords]</i> - Gets a sfw image of a loli, thanks to lolicon.app
Aliases: {prefix}sloli
Can also be activated inline with: @{bot} sfwloli <i>[keywords]</i> or @{bot} sloli <i>[keywords]</i>

{prefix}nsfwloli <i>[keywords]</i> - Gets an nsfw image of a loli, thanks to lolicon.app
Aliases: {prefix}nloli
Can also be activated inline with: @{bot} nsfwloli <i>[keywords]</i> or @{bot} nloli <i>[keywords]</i>''')
