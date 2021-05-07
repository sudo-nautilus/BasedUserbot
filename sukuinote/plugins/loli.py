from pyrogram import Client, filters
from pyrogram.errors.exceptions.forbidden_403 import Forbidden
from .. import slave, config, help_dict, log_errors, public_log_errors

@Client.on_message(~filters.forwarded & ~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(['loli', 'sfwloli', 'sloli', 'nsfwloli', 'nloli'], prefixes=config['config']['prefixes']))
@log_errors
@public_log_errors
async def loli(client, message):
    bot = await slave.get_me()
    query = ' '.join(message.command)
    results = await client.get_inline_bot_results(bot.username or bot.id, query)
    try:
        await message.reply_inline_bot_result(results.query_id, results.results[0].id)
    except Forbidden:
        await message.reply_text({'message': results.results[0].send_message.message, 'entities': results.results[0].send_message.entities}, disable_web_page_preview=True, parse_mode='through')

help_dict['loli'] = ('Loli',
'''{prefix}loli <i>[keywords]</i> - Gets a possibly nsfw image of a loli, thanks to lolicon.app
Can also be activated inline with: @{bot} loli <i>[keywords]</i>

{prefix}sfwloli <i>[keywords]</i> - Gets a sfw image of a loli, thanks to lolicon.app
Aliases: {prefix}sloli
Can also be activated inline with: @{bot} sfwloli <i>[keywords]</i> or @{bot} sloli <i>[keywords]</i>

{prefix}nsfwloli <i>[keywords]</i> - Gets an nsfw image of a loli, thanks to lolicon.app
Aliases: {prefix}nloli
Can also be activated inline with: @{bot} nsfwloli <i>[keywords]</i> or @{bot} nloli <i>[keywords]</i>''')
