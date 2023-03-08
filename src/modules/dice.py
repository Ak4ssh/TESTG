from pyrogram import filters
from pyrogram.types import Message

from src import SUDO, USERBOT_PREFIX, app, app2

ModuleName = "Dice"
HELPS = """
/dice
    Roll a dice.
"""


@app2.on_message(filters.command("dice", prefixes=USERBOT_PREFIX) & SUDO)
@app.on_message(filters.command("dice"))
async def throw_dice(client, message: Message):
    six = (message.from_user.id in SUDO) if message.from_user else False

    c = message.chat.id
    if not six:
        return await client.send_dice(c, "🎲")

    m = await client.send_dice(c, "🎲")

    while m.dice.value != 6:
        await m.delete()
        m = await client.send_dice(c, "🎲")
