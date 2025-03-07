import discord
from discord.ext import commands
from discord import app_commands
import json
import config
import logging
import event_handlers
import uuid

logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s: %(message)s')
logger = logging.getLogger(__name__)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def load_presets():
    try:
        with open("presets.json", "r") as file:
            logger.info("Loading presets from presets.json")
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Failed to load presets: {e}")
        return {}

def save_presets(data):
    with open("presets.json", "w") as file:
        json.dump(data, file, indent=4)
        logger.info("Presets saved to presets.json")

timers = {}
server_presets = load_presets()

# Bot Startup
@bot.event
async def on_ready():
    try:
        await bot.tree.sync()
        logger.info("Slash commands synced.")
    except Exception as e:
        logger.error(f"Failed to sync slash commands: {e}")

    try:
        custom_status = discord.CustomActivity("Expressing myself... Use ! or slash commands!")
        await bot.change_presence(activity=custom_status)
        logger.info("Presence loaded.")
    except Exception as e:
        logger.error(f"Failed to set presence: {e}")

    logger.info(f"Logged in as {bot.user}.")

# Slash Command: Add Preset
@bot.tree.command(name="add_preset", description="Add a new user or phrase trigger preset")
@app_commands.describe(
    trigger_type="Trigger type: user or phrase",
    trigger="User ID, username (mention), or phrase",
    action="Select an action",
    response="Message, GIF URL, or emoji",
    cooldown="Cooldown in minutes"
)
async def add_preset(
    interaction: discord.Interaction,
    trigger_type: str,
    action: str,
    trigger: str,
    response: str,
    cooldown: int
):
    # Automatically lowercase trigger_type and action
    trigger_type = trigger_type.lower()
    action = action.lower()

    logger.info(f"Received add_preset command with trigger_type={trigger_type}, action={action}, trigger={trigger}, response={response}, cooldown={cooldown}")

    # Convert Usernames/Mentions to User IDs if trigger type is "user"
    if trigger_type == "user":
        if trigger.isdigit():
            user_id = trigger  # Already an ID
        else:
            user = discord.utils.get(interaction.guild.members, name=trigger.strip("@"))
            if not user:
                await interaction.response.send_message("User not found!", ephemeral=True)
                logger.warning(f"User not found: {trigger}")
                return
            user_id = str(user.id)
        trigger = user_id  # Save the ID instead of the username

    guild_id = str(interaction.guild.id)
    if guild_id not in server_presets:
        server_presets[guild_id] = []

    preset_id = str(uuid.uuid4())
    preset = {
        "id": preset_id,
        "trigger_type": trigger_type,
        "trigger": trigger,
        "action": action,
        "response": response,
        "cooldown": cooldown,
        "created_by": str(interaction.user)
    }
    server_presets[guild_id].append(preset)
    save_presets(server_presets)
    logger.info(f"Preset added: {preset}")
    await interaction.response.send_message(f"Preset added successfully! ID: {preset_id}", ephemeral=True)

# Choices for the slash command
@add_preset.autocomplete("trigger_type")
async def trigger_type_autocomplete(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name="User", value="user"),
        app_commands.Choice(name="Phrase", value="phrase")
    ]

@add_preset.autocomplete("action")
async def action_autocomplete(interaction: discord.Interaction, current: str):
    return [
        app_commands.Choice(name="Send", value="send"),
        app_commands.Choice(name="Reply", value="reply"),
        app_commands.Choice(name="React", value="react")
    ]

# Import and setup event handlers
event_handlers.setup(bot, server_presets)

bot.run(config.TOKEN)