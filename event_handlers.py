import discord
import logging
import asyncio

from file_handling import load_expressions

logger = logging.getLogger(__name__)

cooldowns = {}


def setup(bot):
    @bot.event
    async def on_message(message: discord.Message):
        if message.author.bot:
            return

        guild_id = str(message.guild.id)
        server_data = load_expressions(guild_id)
        expressions = server_data.get("expressions", [])

        for expression in expressions:
            expression_id = expression["id"]
            trigger_type = expression["trigger_type"]
            trigger = expression["trigger"]
            action = expression["action"]
            response = expression["response"]
            cooldown = expression["cooldown"]

            cooldown_key = f"{guild_id}-{expression_id}"
            if cooldown_key in cooldowns:
                time_left = cooldowns[cooldown_key] - \
                    asyncio.get_event_loop().time()
                if time_left > 0:
                    logger.info(f"Cooldown active for expression {expression_id}: {
                                time_left:.2f} seconds remaining.")
                    continue

            if trigger_type == "user" and str(message.author.id) == trigger:
                await handle_action(message, action, response)
                cooldowns[cooldown_key] = asyncio.get_event_loop().time() + \
                    (cooldown * 60)

            elif trigger_type == "phrase" and trigger.lower() in message.content.lower():
                await handle_action(message, action, response)
                cooldowns[cooldown_key] = asyncio.get_event_loop().time() + \
                    (cooldown * 60)

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
