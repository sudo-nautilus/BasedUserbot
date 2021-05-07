import html
from urllib.parse import quote as urlencode
from pyrogram import Client, filters
from pyrogram.types import InputTextMessageContent, InlineQueryResultArticle, InlineQueryResultPhoto
from .. import log_errors, session, app_user_ids, config

@Client.on_inline_query(filters.regex(f'^(s(?:fw)?|n(?:sfw)?)?loli(.*)$'))
@log_errors
async def loli(client, inline_query):
    if inline_query.from_user.id not in app_user_ids:
        await inline_query.answer([InlineQueryResultArticle('...no', InputTextMessageContent('...no'))], cache_time=3600, is_personal=True)
        return
    match = inline_query.matches[0]
    if mode := match.group(1):
        if mode.startswith('s'):
            mode = 0
        else:
            mode = 1
    else:
        mode = 2
    async with session.get(f'https://api.lolicon.app/setu?num=1&r18={mode}&keyword={urlencode(match.group(2).strip())}&apikey={urlencode(config["config"].get("lolicon_api", ""))}') as resp:
        data = await resp.json()
    if data['code'] or data['msg']:
        item = InlineQueryResultArticle(f'Error {data["code"]}', InputTextMessageContent(f'<b>{html.escape(str(data["code"]))}:</b> {html.escape(data["msg"])}', parse_mode='html'), description=data['msg'] or None)
    else:
        data = data['data'][0]
        title = f'{data["title"]} by {data["author"]}'
        description = None
        caption = f'<a href="https://pixiv.net/artworks/{data["pid"]}">{html.escape(data["title"])}</a> by <a href="https://pixiv.net/users/{data["uid"]}">{html.escape(data["author"])}</a>\n'
        if data['tags']:
            caption += f'<b>Tags:</b> {html.escape(", ".join(data["tags"]))}'
            description = f'Tags: {", ".join(data["tags"])}'
        item = InlineQueryResultPhoto(data['url'], title=title, description=description, caption=caption, parse_mode='html')
    await inline_query.answer([item], cache_time=0)
