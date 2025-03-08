import discord
import logging
import asyncio
import json
import os

logger = logging.getLogger(__name__)

cooldowns = {}

def load_presets(guild_id):
    filepath = f"serverdata/{guild_id}.json"
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load presets for guild {guild_id}: {e}")
            return {"info": {}, "presets": []}
    else:
        return {"info": {}, "presets": []}

def setup(bot):
    @bot.event
    async def on_message(message: discord.Message):
        if message.author.bot:
            return

        guild_id = str(message.guild.id)
        server_data = load_presets(guild_id)
        presets = server_data.get("presets", [])

        for preset in presets:
            preset_id = preset["id"]
            trigger_type = preset["trigger_type"]
            trigger = preset["trigger"]
            action = preset["action"]
            response = preset["response"]
            cooldown = preset["cooldown"]

            cooldown_key = f"{guild_id}-{preset_id}"
            if cooldown_key in cooldowns:
                time_left = cooldowns[cooldown_key] - asyncio.get_event_loop().time()
                if time_left > 0:
                    logger.info(f"Cooldown active for preset {preset_id}: {time_left:.2f} seconds remaining.")
                    continue

            if trigger_type == "user" and str(message.author.id) == trigger:
                await handle_action(message, action, response)
                cooldowns[cooldown_key] = asyncio.get_event_loop().time() + (cooldown * 60)

            elif trigger_type == "phrase" and trigger.lower() in message.content.lower():
                await handle_action(message, action, response)
                cooldowns[cooldown_key] = asyncio.get_event_loop().time() + (cooldown * 60)

    async def handle_action(message, action, response):
        if action == "send":
            await message.channel.send(response)
        elif action == "reply":
            await message.reply(response)
        elif action == "react":
            try:
                await message.add_reaction(response)
            except discord.HTTPException:
                logger.warning(f"Failed to add reaction: {response}")