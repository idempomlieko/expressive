import discord
from discord import app_commands
import logging
import random
import string
import os
import json

logger = logging.getLogger(__name__)

def ensure_serverdata_dir():
    if not os.path.exists("serverdata"):
        os.makedirs("serverdata")

def load_presets(guild_id):
    ensure_serverdata_dir()
    filepath = f"serverdata/{guild_id}.json"
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as file:
                logger.info(f"Loading presets for guild {guild_id} from {filepath}")
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load presets for guild {guild_id}: {e}")
            return {"info": {}, "presets": []}
    else:
        return {"info": {}, "presets": []}

def save_presets(guild_id, data):
    ensure_serverdata_dir()
    filepath = f"serverdata/{guild_id}.json"
    with open(filepath, "w") as file:
        json.dump(data, file, indent=4)
        logger.info(f"Presets for guild {guild_id} saved to {filepath}")

def setup(bot):
    @bot.tree.command(name="expression_new", description="Add a new user or phrase trigger preset")
    @app_commands.describe(
        trigger_type="Trigger type: user or phrase",
        trigger="User ID or phrase",
        action="Select an action",
        response="Message, URL, or emoji",
        cooldown="Cooldown in minutes"
    )
    async def expression_new(
        interaction: discord.Interaction,
        trigger_type: str,
        trigger: str,
        action: str,
        response: str,
        cooldown: int
    ):

        trigger_type = trigger_type.lower()
        action = action.lower()

        logger.info(f"Received expression_new command with trigger_type={trigger_type}, action={action}, trigger={trigger}, response={response}, cooldown={cooldown}")

        if trigger_type == "user":
            if trigger.isdigit():
                user_id = trigger
            else:
                user = discord.utils.get(interaction.guild.members, name=trigger.strip("@"))
                if not user:
                    await interaction.response.send_message("User not found!", ephemeral=True)
                    logger.warning(f"User not found: {trigger}")
                    return
                user_id = str(user.id)
            trigger = user_id

        guild_id = str(interaction.guild.id)
        server_data = load_presets(guild_id)
        if "info" not in server_data or not server_data["info"]:
            server_data["info"] = {
                "id": guild_id,
                "name": interaction.guild.name,
                "invited_at": str(interaction.guild.me.joined_at)
            }

        preset_id = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
        preset = {
            "id": preset_id,
            "trigger_type": trigger_type,
            "trigger": trigger,
            "action": action,
            "response": response,
            "cooldown": cooldown,
            "created_by": str(interaction.user)
        }
        server_data["presets"].append(preset)
        save_presets(guild_id, server_data)
        logger.info(f"Preset added: {preset}")
        await interaction.response.send_message(f"Preset added successfully! ID: {preset_id}", ephemeral=True)

    @expression_new.autocomplete("trigger_type")
    async def trigger_type_autocomplete(interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name="User", value="user"),
            app_commands.Choice(name="Phrase", value="phrase")
        ]

    @expression_new.autocomplete("action")
    async def action_autocomplete(interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name="Send", value="send"),
            app_commands.Choice(name="Reply", value="reply"),
            app_commands.Choice(name="React", value="react")
        ]

    @bot.tree.command(name="help", description="Show all available commands")
    async def help_command(interaction: discord.Interaction):
        commands_list = """
        **Available Commands:**
        - /help: Show all available commands
        - /expressive: Show all available commands
        - /expression_new: Create a new expression preset
        - /expression_guide: Show a guide on how to make expressions
        - /expression_list: Show a list of all expressions on the server
        """
        await interaction.response.send_message(commands_list, ephemeral=True)

    @bot.tree.command(name="expressive", description="Show all available commands")
    async def expressive_command(interaction: discord.Interaction):
        await help_command(interaction)

    @bot.tree.command(name="expression_guide", description="Show a guide on how to make expressions")
    async def expression_guide(interaction: discord.Interaction):
        guide = """
        **Guide to Creating Expressions:**
        1. Use the /expression_new command to create a new expression preset.
        2. Provide the trigger type (user or phrase), trigger, action, response, and cooldown.
        3. The bot will respond with a confirmation message and the preset ID.
        """
        await interaction.response.send_message(guide, ephemeral=True)

    @bot.tree.command(name="expression_list", description="Show a list of all expressions on the server")
    async def expression_list(interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        server_data = load_presets(guild_id)
        if not server_data["presets"]:
            await interaction.response.send_message("No expressions found for this server.", ephemeral=True)
            return

        expressions = server_data["presets"]
        expressions_list = "\n".join([f"ID: {exp['id']}, Trigger: {exp['trigger']}, Action: {exp['action']}, Response: {exp['response']}" for exp in expressions])
        await interaction.response.send_message(f"**Expressions List:**\n{expressions_list}", ephemeral=True)