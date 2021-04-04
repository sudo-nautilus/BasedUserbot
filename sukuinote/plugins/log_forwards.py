import html
import asyncio
from collections import defaultdict
from pyrogram import Client, filters
from .. import config, log_errors, app_user_ids, log_ring

logged = defaultdict(set)
lock = asyncio.Lock()
force_ltr = '\u200E'

@Client.on_message(~filters.chat(config['config']['log_chat']) & filters.incoming & filters.forwarded & (filters.group | filters.channel))
@log_errors
async def log_forwards(client, message):
    if not config['config'].get('log_forwards'):
        return
    if getattr(message.from_user, 'id', None) in app_user_ids:
        return
    for i in app_user_ids:
        if message.forward_from:
            if i == message.forward_from.id:
                forwardee = app_user_ids[i]
                break
        j = app_user_ids[i].first_name
        if app_user_ids[i].last_name:
            j += f' {app_user_ids[i].last_name}'
        if j == message.forward_sender_name:
            forwardee = app_user_ids[i]
            break
    else:
        return
    async with lock:
        if message.message_id in logged[message.chat.id]:
            return
        chat_text = html.escape(message.chat.title)
        if message.chat.username:
            chat_text = f'<a href="https://t.me/{message.chat.username}">{chat_text}</a>'
        text = f'<b>Forwarded Event</b>\n- <b>Chat:</b> {chat_text}{force_ltr} '
        if message.chat.is_verified:
            chat_text += '<code>[VERIFIED]</code> '
        if message.chat.is_support:
            chat_text += '<code>[SUPPORT]</code> '
        if message.chat.is_scam:
            chat_text += '<code>[SCAM]</code> '
        if getattr(message.chat, 'is_fake', None):
            chat_text += '<code>[FAKE]</code> '
        text += f'[<code>{message.chat.id}</code>]'
        if message.chat.type != 'channel':
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
            text += f'\n- <b>Forwarder:</b> {user_text}{force_ltr}'
        text += f'\n- <b><a href="{message.link}">Message'
        mtext = (message.text or message.caption or '').strip()
        if mtext:
            text += ':'
        text += '</a></b>'
        if mtext:
            text += f' {html.escape(mtext.strip()[:2000])}{force_ltr}'
        text += '\n- <b>Forwardee:</b> '
        user_text = forwardee.first_name
        if forwardee.last_name:
            user_text += f' {forwardee.last_name}'
        user_text = '<code>[DELETED]</code>' if forwardee.is_deleted else html.escape(user_text or 'Empty???')
        if forwardee.is_verified:
            user_text += ' <code>[VERIFIED]</code>'
        if forwardee.is_support:
            user_text += ' <code>[SUPPORT]</code>'
        if forwardee.is_scam:
            user_text += ' <code>[SCAM]</code>'
        if getattr(forwardee, 'is_fake', None):
            user_text += ' <code>[FAKE]</code>'
        text += f'{user_text}{force_ltr} [<code>{forwardee.id}</code>]'
        log_ring.append(text)
        logged[message.chat.id].add(message.message_id)
