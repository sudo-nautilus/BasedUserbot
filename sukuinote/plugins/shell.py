import re
import html
import asyncio
from io import BytesIO
from pyrogram import Client, filters
from .. import config, help_dict, log_errors, public_log_errors

SHELL_REGEX = '^(?:' + '|'.join(map(re.escape, config['config']['prefixes'])) + r')(?:(?:ba)?sh|shell|term(?:inal)?)\s+(.+)(?:\n([\s\S]+))?$'
@Client.on_message(~filters.forwarded & ~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.regex(SHELL_REGEX))
@log_errors
@public_log_errors
async def shell(client, message):
    match = re.match(SHELL_REGEX, (message.text or message.caption).markdown)
    if not match:
        return
    command = match.group(1)
    stdin = match.group(2)
    reply = await message.reply_text('Executing...')
    process = await asyncio.create_subprocess_shell(command, stdin=asyncio.subprocess.PIPE if stdin else None, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT)
    stdout, _ = await process.communicate(stdin.encode() if stdin else None)
    returncode = process.returncode
    text = f'<b>Exit Code:</b> <code>{returncode}</code>\n'
    stdout = stdout.decode().replace('\r', '').strip('\n').rstrip()
    if stdout:
        text += f'<code>{html.escape(stdout)}</code>'

    # send as a file if it's longer than 4096 bytes
    if len(text) > 4096:
        f = BytesIO(stdout.encode('utf-8'))
        f.name = "output.txt"
        await reply.delete()
        await message.reply_document(f, caption=f'<b>Exit Code:</b> <code>{returncode}</code>')
    else:
        await reply.edit_text(text)

help_dict['shell'] = ('Shell',
'''{prefix}sh <i>&lt;command&gt;</i> \\n <i>[stdin]</i> - Executes <i>&lt;command&gt;</i> in shell
Aliases: {prefix}bash, {prefix}shell, {prefix}term, {prefix}terminal''')
