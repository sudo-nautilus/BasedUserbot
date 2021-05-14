import html
import asyncio
from collections import defaultdict
from pyrogram import Client, filters
from .. import config, log_errors, log_ring

reported = defaultdict(set)
lock = asyncio.Lock()
force_ltr = '\u200E'

@Client.on_message(~filters.chat(config['config']['log_chat']) & filters.regex(r'(?:^|\s+)@admins?(?:$|\W+)|^[/!#](?:report|admins?)(?:$|\W+)') & filters.group)
@log_errors
async def log_reports(client, message):
    if not config['config']['log_reports']:
        return
    async with lock:
        if message.message_id in reported[message.chat.id]:
            return
        chat_text = html.escape(message.chat.title)
        if message.chat.username:
            chat_text = f'<a href="https://t.me/{message.chat.username}">{chat_text}</a>'
        text = f'<b>Report Event</b>\n- <b>Chat:</b> {chat_text}{force_ltr} '
        if message.chat.is_verified:
            chat_text += '<code>[VERIFIED]</code> '
        if message.chat.is_support:
            chat_text += '<code>[SUPPORT]</code> '
        if message.chat.is_scam:
            chat_text += '<code>[SCAM]</code> '
        if getattr(message.chat, 'is_fake', None):
            chat_text += '<code>[FAKE]</code> '
        text += f'[<code>{message.chat.id}</code>]\n- <b>Reporter:</b> '
        if message.from_user:
            user_text = message.from_user.first_name
            if message.from_user.last_name:
                user_text += f' {message.from_user.last_name}'
            user_text = '<code>[DELETED]</code>' if message.from_user.is_deleted else html.escape(user_text or 'Empty???')
            if message.from_user.is_verified:
                user_text += ' <code>[VERIFIED]</code>'
            if message.from_user.is_support:
                user_text += ' <code>[SUPPORT]</code>'
            if message.from_user.is_scam:
                user_text += ' <code>[SCAM]</code>'
            if getattr(message.from_user, 'is_fake', None):
                user_text += ' <code>[FAKE]</code>'
            user_text += f' [<code>{message.from_user.id}</code>]'
        elif message.sender_chat and message.sender_chat.id != message.chat.id:
            user_text = html.escape(message.sender_chat.title)
            if message.sender_chat.username:
                user_text = f'<a href="https://t.me/{message.sender_chat.username}">{user_text}</a>'
            if message.sender_chat.is_verified:
                user_text += ' <code>[VERIFIED]</code>'
            if message.sender_chat.is_support:
                user_text += ' <code>[SUPPORT]</code>'
            if message.sender_chat.is_scam:
                user_text += ' <code>[SCAM]</code>'
            if getattr(message.sender_chat, 'is_fake', None):
                user_text += ' <code>[FAKE]</code>'
        else:
            user_text = 'Anonymous'
        text += f'{user_text}{force_ltr}\n'
        start, end = message.matches[0].span()
        text += f'- <b><a href="{message.link}">Report Message'
        mtext = (message.text or message.caption or '').strip()
        if start or end < len(mtext):
            text += ':'
        text += '</a></b>'
        if start or end < len(mtext):
            text += f' {html.escape(mtext.strip()[:1000])}{force_ltr}'
        reply = message.reply_to_message
        if not getattr(reply, 'empty', True):
            text += '\n- <b>Reportee:</b> '
            if reply.from_user:
                user_text = reply.from_user.first_name
                if reply.from_user.last_name:
                    user_text += f' {reply.from_user.last_name}'
                user_text = '<code>[DELETED]</code>' if reply.from_user.is_deleted else html.escape(user_text or 'Empty???')
                if reply.from_user.is_verified:
                    user_text += ' <code>[VERIFIED]</code>'
                if reply.from_user.is_support:
                    user_text += ' <code>[SUPPORT]</code>'
                if reply.from_user.is_scam:
                    user_text += ' <code>[SCAM]</code>'
                if getattr(reply.from_user, 'is_fake', None):
                    user_text += ' <code>[FAKE]</code>'
                user_text += f' [<code>{reply.from_user.id}</code>]'
            elif reply.sender_chat and reply.sender_chat.id != reply.chat.id:
                user_text = html.escape(reply.sender_chat.title)
                if reply.sender_chat.username:
                    user_text = f'<a href="https://t.me/{reply.sender_chat.username}">{user_text}</a>'
                if reply.sender_chat.is_verified:
                    user_text += ' <code>[VERIFIED]</code>'
                if reply.sender_chat.is_support:
                    user_text += ' <code>[SUPPORT]</code>'
                if reply.sender_chat.is_scam:
                    user_text += ' <code>[SCAM]</code>'
                if getattr(reply.sender_chat, 'is_fake', None):
                    user_text += ' <code>[FAKE]</code>'
            else:
                user_text = 'Anonymous'
            text += f'{user_text}{force_ltr}\n- <b><a href="{reply.link}">Reported Message'
            mtext = reply.text or reply.caption or ''
            if mtext.strip():
                text += ':'
            text += f'</a></b> {html.escape(mtext.strip()[:1000])}{force_ltr}'
        log_ring.append(text)
        reported[message.chat.id].add(message.message_id)
