# https://greentreesnakes.readthedocs.io/
import re
import ast
import sys
import html
import inspect
import asyncio
from io import StringIO, BytesIO
from pyrogram import Client, filters
from .. import config, help_dict, log_errors, slave, apps, session, public_log_errors

exec_tasks = dict()

PYEXEC_REGEX = '^(?:' + '|'.join(map(re.escape, config['config']['prefixes'])) + r')exec\s+([\s\S]+)$'
@Client.on_message(~filters.forwarded & ~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.regex(PYEXEC_REGEX))
@log_errors
@public_log_errors
async def pyexec(client, message):
    match = re.match(PYEXEC_REGEX, (message.text or message.caption).markdown)
    if not match:
        return
    code = match.group(1).strip()
    class UniqueExecReturnIdentifier:
        pass
    tree = ast.parse(code)
    obody = tree.body
    body = obody.copy()
    body.append(ast.Return(ast.Name('_ueri', ast.Load())))
    def _gf(body):
        # args: c, client, m, message, executing, r, reply, _ueri
        func = ast.AsyncFunctionDef('ex', ast.arguments([], [ast.arg(i, None, None) for i in ['c', 'client', 'm', 'message', 'executing', 'r', 'reply', '_ueri']], None, [], [], None, []), body, [], None, None)
        ast.fix_missing_locations(func)
        mod = ast.parse('')
        mod.body = [func]
        fl = locals().copy()
        exec(compile(mod, '<ast>', 'exec'), globals(), fl)
        return fl['ex']
    try:
        exx = _gf(body)
    except SyntaxError as ex:
        if ex.msg != "'return' with value in async generator":
            raise
        exx = _gf(obody)
    rnd_id = client.rnd_id()
    reply = await message.reply_text(f'Executing <code>{rnd_id}</code>...')
    oasync_obj = exx(client, client, message, message, reply, message.reply_to_message, message.reply_to_message, UniqueExecReturnIdentifier)
    if inspect.isasyncgen(oasync_obj):
        async def async_obj():
            return [i async for i in oasync_obj]
    else:
        async def async_obj():
            to_return = [await oasync_obj]
            return [] if to_return == [UniqueExecReturnIdentifier] else to_return
    stdout = sys.stdout
    stderr = sys.stderr
    wrapped_stdout = StringIO()
    try:
        sys.stdout = sys.stderr = wrapped_stdout
        task = asyncio.create_task(async_obj())
        exec_tasks[rnd_id] = task
        returned = await task
    except asyncio.CancelledError:
        sys.stdout = stdout
        sys.stderr = stderr
        exec_tasks.pop(rnd_id, None)
        await reply.edit_text('Cancelled')
        return
    finally:
        sys.stdout = stdout
        sys.stderr = stderr
        exec_tasks.pop(rnd_id, None)
    wrapped_stderr.seek(0)
    wrapped_stdout.seek(0)
    output = ''
    wrapped_stdout_text = wrapped_stdout.read().strip()
    if wrapped_stdout_text:
        output += f'<code>{html.escape(wrapped_stdout_text)}</code>\n'
    for i in returned:
        output += f'<code>{html.escape(str(i).strip())}</code>\n'
    if not output.strip():
        output = 'Executed'
    
    # send as a file if it's longer than 4096 bytes
    if len(output) > 4096:
        out = wrapped_stdout_text + "\n"
        for i in returned:
            out += str(i).strip() + "\n"
        f = BytesIO(out.strip().encode('utf-8'))
        f.name = "output.txt"
        await reply.delete()
        await message.reply_document(f)
    else:
        await reply.edit_text(output)

@Client.on_message(~filters.forwarded & ~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(['listexecs', 'listexec', 'lexec'], prefixes=config['config']['prefixes']))
@log_errors
@public_log_errors
async def listexec(client, message):
    text = '\n'.join(map(str, exec_tasks))
    if len(text) > 4096:
        f = BytesIO(text.encode('utf-8'))
        f.name = 'exectasks.txt'
        await message.reply_document(f)
    else:
        text = '\n'.join(map(lambda i: f'<code>{i}</code>', exec_tasks))
        await message.reply_text(text or 'No tasks')

@Client.on_message(~filters.forwarded & ~filters.sticker & ~filters.via_bot & ~filters.edited & filters.me & filters.command(['cancelexec', 'cexec'], prefixes=config['config']['prefixes']))
@log_errors
@public_log_errors
async def cancelexec(client, message):
    try:
        task = exec_tasks.get(int(message.command[1]))
    except IndexError:
        return
    if not task:
        await message.reply_text('Task does not exist')
        return
    task.cancel()

help_dict['exec'] = ('Exec', '''{prefix}exec <i>&lt;python code&gt;</i> - Executes python code

{prefix}listexecs - List exec tasks
Aliases: {prefix}listexec, {prefix}lexec

{prefix}cancelexec <i>&lt;task id&gt;</i> - Cancel exec task
Aliases: {prefix}cexec''')
