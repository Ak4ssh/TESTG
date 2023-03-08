"""
MIT License

Copyright (c) 2023 TheVenomXD

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import asyncio
import time
from inspect import getfullargspec
from os import path

from aiohttp import ClientSession
from motor.motor_asyncio import AsyncIOMotorClient as MongoClient
from pyrogram import Client, filters
from pyrogram.types import Message
from pyromod import listen
from Python_ARQ import ARQ
from telegraph import Telegraph

is_config = path.exists("config.py")

if is_config:
    from config import *
else:
    from sample_config import *

USERBOT_PREFIX = USERBOT_PREFIX
GBAN_LOG_GROUP_ID = GBAN_LOG_GROUP_ID
WELCOME_DELAY_KICK_SEC = WELCOME_DELAY_KICK_SEC
LOG_GROUP_ID = LOG_GROUP_ID
MESSAGE_DUMP_CHAT = MESSAGE_DUMP_CHAT
MOD_LOAD = []
MOD_NOLOAD = []
SUDO = filters.user()
bot_start_time = time.time()


class Log:
    def __init__(self, save_to_file=False, file_name="src.log"):
        self.save_to_file = save_to_file
        self.file_name = file_name

    def info(self, msg):
        print(f"[+]: {msg}")
        if self.save_to_file:
            with open(self.file_name, "a") as f:
                f.write(f"[INFO]({time.ctime(time.time())}): {msg}\n")

    def error(self, msg):
        print(f"[-]: {msg}")
        if self.save_to_file:
            with open(self.file_name, "a") as f:
                f.write(f"[ERROR]({time.ctime(time.time())}): {msg}\n")


log = Log(True, "bot.log")

# MongoDB client
log.info("Initializing MongoDB client")
mongo_client = MongoClient(MONGO_URL)
db = mongo_client.src


async def load_SUDO():
    global SUDO
    log.info("Loading SUDO")
    SUDOdb = db.SUDO
    SUDO = await SUDOdb.find_one({"sudo": "sudo"})
    SUDO = [] if not SUDO else SUDO["SUDO"]
    for user_id in SUDO_USERS_ID:
        SUDO.add(user_id)
        if user_id not in SUDO:
            SUDO.append(user_id)
            await SUDOdb.update_one(
                {"sudo": "sudo"},
                {"$set": {"SUDO": SUDO}},
                upsert=True,
            )
    if SUDO:
        for user_id in SUDO:
            SUDO.add(user_id)


loop = asyncio.get_event_loop()
loop.run_until_complete(load_SUDO())

if not SESSION_STRING:
    app2 = Client(
        name="userbot",
        api_id=API_ID,
        api_hash=API_HASH,
        phone_number=PHONE_NUMBER,
    )
else:
    app2 = Client(
        name="userbot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING
    )

aiohttpsession = ClientSession()

arq = ARQ(ARQ_API_URL, ARQ_API_KEY, aiohttpsession)

app = Client("src", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

log.info("Starting bot client")
app.start()
log.info("Starting userbot client")
app2.start()

log.info("Gathering profile info")
x = app.get_me()
y = app2.get_me()

BOT_ID = x.id
BOT_NAME = x.first_name + (x.last_name or "")
BOT_USERNAME = x.username
BOT_MENTION = x.mention
BOT_DC_ID = x.dc_id

BOT_ID = y.id
USERBOT_NAME = y.first_name + (y.last_name or "")
USERBOT_USERNAME = y.username
USERBOT_MENTION = y.mention
USERBOT_DC_ID = y.dc_id

if BOT_ID not in SUDO:
    SUDO.add(BOT_ID)

log.info("Initializing Telegraph client")
telegraph = Telegraph()
telegraph.create_account(short_name=BOT_USERNAME)


async def eor(msg: Message, **kwargs):
    func = (
        (msg.edit_text if msg.from_user.is_self else msg.reply)
        if msg.from_user
        else msg.reply
    )
    spec = getfullargspec(func.__wrapped__).args
    return await func(**{k: v for k, v in kwargs.items() if k in spec})