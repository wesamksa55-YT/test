import os
import asyncio
import logging

import discord
from discord.ext import tasks, commands

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("spam-bot")

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("DISCORD_TOKEN environment variable is required")

DEFAULT_MESSAGE = "هذه رسالة تلقائية."
SECONDS_BETWEEN_CHANNELS = 1
LOOP_INTERVAL_SECONDS = 1

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix=".", intents=intents)
message_to_send = DEFAULT_MESSAGE
task_started_by = None

# ====== حدث تشغيل البوت ======
@bot.event
async def on_ready():
    global task_started_by
    log.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    if not send_every_second.is_running():
        task_started_by = "بوت تلقائي"
        send_every_second.start()
        log.info("تم بدء المهمة الدورية تلقائيًا عند تشغيل البوت.")

# ====== المهمة الدورية ======
@tasks.loop(seconds=LOOP_INTERVAL_SECONDS)
async def send_every_second():
    global message_to_send
    for guild in bot.guilds:
        me = guild.get_member(bot.user.id)
        for channel in guild.text_channels:
            try:
                perms = channel.permissions_for(me)
                if not perms.send_messages or not perms.mention_everyone:
                    continue
                await channel.send(f"@everyone {message_to_send}")
                await asyncio.sleep(SECONDS_BETWEEN_CHANNELS)
            except Exception as e:
                log.exception(f"Error in {guild.name}/{channel.name}: {e}")

# ====== أوامر البوت ======
@bot.command(name="pause")
async def _pause(ctx):
    if send_every_second.is_running():
        send_every_second.stop()
        await ctx.send("تم إيقاف المهمة الدورية مؤقتًا.")
    else:
        await ctx.send("المهمة الدورية متوقفة بالفعل.")

@bot.command(name="setmessage")
async def _setmessage(ctx, *, new_message: str):
    global message_to_send
    message_to_send = new_message
    await ctx.send("تم تحديث رسالة البوت.")

@bot.command(name="commands")
async def _commands(ctx):
    help_text = (
        "**أوامر البوت:**\n"
        "`.pause` - إيقاف المهمة مؤقتًا.\n"
        "`.setmessage <النص>` - تغيير رسالة البوت.\n"
        "`.commands` - عرض قائمة الأوامر."
    )
    await ctx.send(help_text)

bot.run(TOKEN)
