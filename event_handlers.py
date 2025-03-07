import discord
import logging
import asyncio

logger = logging.getLogger(__name__)

cooldowns = {}  # Dictionary to store active cooldowns

def setup(bot, server_presets):
    @bot.event
    async def on_message(message: discord.Message):
        if message.author.bot:
            return  # Ignore bot messages

        guild_id = str(message.guild.id)
        if guild_id not in server_presets:
            return

        presets = server_presets[guild_id]

        for preset in presets:
            preset_id = preset["id"]
            trigger_type = preset["trigger_type"]
            trigger = preset["trigger"]
            action = preset["action"]
            response = preset["response"]
            cooldown = preset["cooldown"]

            # Check cooldown
            cooldown_key = f"{guild_id}-{preset_id}"
            if cooldown_key in cooldowns:
                time_left = cooldowns[cooldown_key] - asyncio.get_event_loop().time()
                if time_left > 0:
                    logger.info(f"Cooldown active for preset {preset_id}: {time_left:.2f} seconds remaining.")
                    continue  # Skip this preset if it's on cooldown

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
                await message.add_reaction(response)  # Response should be an emoji
            except discord.HTTPException:
                logger.warning(f"Failed to add reaction: {response}")