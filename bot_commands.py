import discord
from discord import app_commands
from datetime import datetime
import logging
import random
import string

from file_handling import load_expressions, save_expressions

logger = logging.getLogger(__name__)

icon_url = "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fimg.freepik.com%2Fpremium-photo%2Fespresso-with-white-background_985067-3129.jpg%3Fw%3D2000&f=1&nofb=1&ipt=903c7ea5acb50a1c4c929321fb543b89e1ea79a8b9d7787c9555edea80b3f4bc&ipo=images"


def setup(bot):
    @bot.tree.command(name="expression_new", description="Add a new user or phrase trigger expression")
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

        logger.info(f"Received expression_new command with trigger_type={trigger_type}, action={
                    action}, trigger={trigger}, response={response}, cooldown={cooldown}")

        if trigger_type == "user":
            if trigger.isdigit():
                user_id = trigger
            else:
                user = discord.utils.get(
                    interaction.guild.members, name=trigger.strip("@"))
                if not user:
                    await interaction.response.send_message("User not found!", ephemeral=True)
                    logger.warning(f"User not found: {trigger}")
                    return
                user_id = str(user.id)
            trigger = user_id

        guild_id = str(interaction.guild.id)
        server_data = load_expressions(guild_id)
        if "info" not in server_data or not server_data["info"]:
            server_data["info"] = {
                "id": guild_id,
                "name": interaction.guild.name,
                "invited_at": str(interaction.guild.me.joined_at)
            }

        expression_id = ''.join(random.choices(
            string.ascii_letters + string.digits, k=5))
        expression = {
            "id": expression_id,
            "trigger_type": trigger_type,
            "trigger": trigger,
            "action": action,
            "response": response,
            "cooldown": cooldown,
            "created_by": str(interaction.user)
        }
        server_data["expressions"].append(expression)
        save_expressions(guild_id, server_data)
        logger.info(f"Expression added: {expression}")
        await interaction.response.send_message(f"Expression added successfully! ID: {expression_id}", ephemeral=True)

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
        embed = discord.Embed(
            title="**Expressive** help",
            description=(
                "**/help** - Show all available commands\n"
                "**/expression_new** - Create a new expression\n"
                "**/expression_guide** - Show a guide on how to make expressions\n"
                "**/expression_list** - Show a list of all expressions on the server\n"
                "**/expression_delete** - Delete an expression by ID"
            ),

            colour=0xc15bb2,
            timestamp=datetime.now()
        )

        embed.set_footer(
            text="Expressive",
            icon_url=icon_url
        )

        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="expression_guide", description="Show a guide on how to make expressions")
    async def expression_guide(interaction: discord.Interaction):
        embed = discord.Embed(
            title="**Expressive** expression guide",
            description=(
                "**1.** Use the /expression_new command to create a new expression.\n"
                "**2.** Provide the trigger type (user or phrase), trigger, action, response, and cooldown.\n"
                "**3.** The bot will respond with a confirmation message and the expression ID.\n"
            ),

            colour=0xc15bb2,
            timestamp=datetime.now()
        )

        embed.set_footer(
            text="Expressive",
            icon_url=icon_url
        )

        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="expression_list", description="Show a list of all expressions on the server")
    async def expression_list(interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        server_data = load_expressions(guild_id)
        expressions = server_data["expressions"]

        if not expressions:
            embed = discord.Embed(
                title="**Expressive** expression list",
                description=(
                    "No expressions found for this server."
                ),

                colour=0xc15bb2,
                timestamp=datetime.now()
            )
        else:
            embed = discord.Embed(
                title="**Expressive** expression list",
                colour=0xc15bb2,
                timestamp=datetime.now()
            )

            description_lines = []

            for exp in expressions:
                trigger = exp['trigger']

                # Convert user ID to username
                if exp['trigger_type'] == "user":
                    user = bot.get_user(int(trigger))
                    if user is None:
                        try:
                            user = await bot.fetch_user(int(trigger))
                        except discord.NotFound:
                            user = None

                    trigger = user.name if user else trigger

                description_lines.append(
                    f"**ID:** {exp['id']}, "
                    f"**Type:** {exp['trigger_type']}, "
                    f"**Trigger:** {trigger}, "
                    f"**Action:** {exp['action']}, "
                    f"**Response:** {exp['response']}"
                )

            embed.description = "\n".join(description_lines)

        embed.set_footer
        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="expression_delete", description="Delete an expression by ID")
    @app_commands.describe(expression_id="The ID of the expression to delete")
    async def expression_delete(interaction: discord.Interaction, expression_id: str):
        guild_id = str(interaction.guild.id)
        server_data = load_expressions(guild_id)
        expressions = server_data.get("expressions", [])

        expression_to_delete = next(
            (exp for exp in expressions if exp["id"] == expression_id), None)
        if expression_to_delete:
            expressions.remove(expression_to_delete)
            save_expressions(guild_id, server_data)
            logger.info(f"Expression deleted: {expression_to_delete}")
            await interaction.response.send_message(f"Expression with ID {expression_id} deleted successfully.", ephemeral=True)
        else:
            await interaction.response.send_message(f"No expression found with ID {expression_id}.", ephemeral=True)
