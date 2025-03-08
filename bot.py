import discord
from discord.ext import commands
import config
import logging
import event_handlers
import commands

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
        custom_status = discord.CustomActivity("Expressing myself... Use slash commands!")
        await bot.change_presence(activity=custom_status)
        logger.info("Presence loaded.")
    except Exception as e:
        logger.error(f"Failed to set presence: {e}")

    logger.info(f"Logged in as {bot.user}.")


event_handlers.setup(bot)
commands.setup(bot)

bot.run(config.TOKEN)