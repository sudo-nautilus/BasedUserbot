import html
import asyncio
import logging
import traceback
from pyrogram import idle
from pyrogram.errors.exceptions.flood_420 import FloodWait
from . import loop, apps, slave, app_user_ids, session, log_ring, config

async def main():
    async def _start_app(app):
        await app.start()
        asyncio.create_task(_get_me_loop(app))
    async def _get_me_loop(app):
        while True:
            try:
                me = await app.get_me()
                app_user_ids[me.id] = me
            except BaseException:
                pass
            await asyncio.sleep(60)
    async def log_ring_worker():
        while True:
            await asyncio.sleep(1)
            try:
                text = log_ring.popleft()
            except IndexError:
                pass
            else:
                while True:
                    try:
                        await slave.send_message(config['config']['log_chat'], text, disable_web_page_preview=True)
                    except FloodWait as ex:
                        await asyncio.sleep(ex.x + 1)
                    except BaseException:
                        logging.exception('Exception occured while sending message to log chat')
                        log_ring.append(f'Exception occured while sending message to log chat\n\n{html.escape(traceback.format_exc())}')
                    else:
                        break
    asyncio.create_task(log_ring_worker())
    await asyncio.gather(*(_start_app(app) for app in apps), slave.start())
    await idle()
    await asyncio.gather(*(app.stop() for app in apps), slave.stop())
    await session.close()

loop.run_until_complete(main())
