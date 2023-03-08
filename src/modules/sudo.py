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
from pyrogram import filters
from pyrogram.types import Message

from src import BOT_ID, SUDO, USERBOT_PREFIX, app2, eor
from src.core.decorators.errors import capture_err
from src.utils.dbfunctions import add_sudo, get_SUDO, remove_sudo

ModuleName = "Sudo"
HELPS = """
**THIS MODULE IS ONLY FOR DEVS**

.useradd - To Add A User In SUDO.
.userdel - To Remove A User From SUDO.
.SUDO - To List Sudo Users.

**NOTE:**

Never add anyone to SUDO unless you trust them,
sudo users can do anything with your account, they
can even delete your account.
"""


@app2.on_message(filters.command("useradd", prefixes=USERBOT_PREFIX) & SUDO)
@capture_err
async def useradd(_, message: Message):
    if not message.reply_to_message:
        return await eor(
            message,
            text="Reply to someone's message to add him to SUDO.",
        )
    user_id = message.reply_to_message.from_user.id
    umention = (await app2.get_users(user_id)).mention
    SUDO = await get_SUDO()

    if user_id in SUDO:
        return await eor(message, text=f"{umention} is already in SUDO.")
    if user_id == BOT_ID:
        return await eor(message, text="You can't add assistant bot in SUDO.")

    await add_sudo(user_id)

    if user_id not in SUDO:
        SUDO.add(user_id)

    await eor(
        message,
        text=f"Successfully added {umention} in SUDO.",
    )


@app2.on_message(filters.command("userdel", prefixes=USERBOT_PREFIX) & SUDO)
@capture_err
async def userdel(_, message: Message):
    if not message.reply_to_message:
        return await eor(
            message,
            text="Reply to someone's message to remove him to SUDO.",
        )
    user_id = message.reply_to_message.from_user.id
    umention = (await app2.get_users(user_id)).mention

    if user_id not in await get_SUDO():
        return await eor(message, text=f"{umention} is not in SUDO.")

    await remove_sudo(user_id)

    if user_id in SUDO:
        SUDO.remove(user_id)

    await eor(
        message,
        text=f"Successfully removed {umention} from SUDO.",
    )


@app2.on_message(filters.command("SUDO", prefixes=USERBOT_PREFIX) & SUDO)
@capture_err
async def SUDO_list(_, message: Message):
    SUDO = await get_SUDO()
    text = ""
    j = 0
    for user_id in SUDO:
        try:
            user = await app2.get_users(user_id)
            user = user.first_name if not user.mention else user.mention
            j += 1
        except Exception:
            continue
        text += f"{j}. {user}\n"
    if text == "":
        return await eor(message, text="No SUDO found.")
    await eor(message, text=text)
