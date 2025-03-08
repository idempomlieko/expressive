import discord
from discord.ext import commands
import config
import logging
import event_handlers
import bot_commands

logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
        logger.info("Slash commands synced.")
    except Exception as e:
        logger.error(f"Failed to sync slash commands: {e}")

    try:
        server_count = len(bot.guilds)
        custom_status = discord.Game(f"Expressing myself in {server_count} servers!")
        await bot.change_presence(activity=custom_status)
        logger.info("Presence loaded.")
    except Exception as e:
        logger.error(f"Failed to set presence: {e}")

    logger.info(f"Logged in as {bot.user}.")

event_handlers.setup(bot)
bot_commands.setup(bot)

bot.run(config.TOKEN)