import discord
from discord import app_commands
from discord.ui import View, Button, Select
from datetime import datetime
import logging
import random
import string

from file_handling import load_expressions, save_expressions

logger = logging.getLogger(__name__)

icon_url = "https://media.discordapp.net/attachments/568378850929803274/1349836095029907497/expressive_logo.png?ex=67d48c53&is=67d33ad3&hm=e61ad04e6b7d0b0d306c104d35c48bfbb6474ea4273d0b14cb040d0656d3b6af&=&width=438&height=438"
embed_color = 0xc15bb2
footer_text = "Expressive"

class ExpressionSelect(Select):
    def __init__(self, expressions):
        options = [
            discord.SelectOption(label=exp['id'], description=exp['trigger'])
            for exp in expressions
        ]
        super().__init__(placeholder="Select an expression...", options=options)

    async def callback(self, interaction: discord.Interaction):
        selected_id = self.values[0]
        guild_id = str(interaction.guild.id)
        server_data = load_expressions(guild_id)
        expression = next((exp for exp in server_data["expressions"] if exp["id"] == selected_id), None)

        if expression:
            embed = discord.Embed(
                title=f"Expression Details - {expression['id']}",
                colour=embed_color,
                timestamp=datetime.now()
            )
            embed.add_field(name="Trigger Type", value=expression["trigger_type"], inline=True)
            embed.add_field(name="Trigger", value=expression["trigger"], inline=True)
            embed.add_field(name="Action", value=expression["action"], inline=True)
            embed.add_field(name="Response", value=expression["response"], inline=True)
            embed.add_field(name="Cooldown", value=f"{expression['cooldown']} minutes", inline=True)
            embed.add_field(name="Created By", value=expression["created_by"], inline=True)
            embed.set_footer(text=footer_text, icon_url=icon_url)

            await interaction.response.send_message(embed=embed, ephemeral=True)

class Paginator(View):
    def __init__(self, expressions, page_size=10):
        super().__init__(timeout=None)
        self.expressions = expressions
        self.page_size = page_size
        self.current_page = 0

        self.left_button = Button(label="⬅️", style=discord.ButtonStyle.primary)
        self.right_button = Button(label="➡️", style=discord.ButtonStyle.primary)

        self.left_button.callback = self.previous_page
        self.right_button.callback = self.next_page

        self.add_item(self.left_button)
        self.add_item(self.right_button)
        self.add_item(ExpressionSelect(expressions))

    async def previous_page(self, interaction: discord.Interaction):
        if self.current_page > 0:
            self.current_page -= 1
            await self.update_message(interaction)

    async def next_page(self, interaction: discord.Interaction):
        if (self.current_page + 1) * self.page_size < len(self.expressions):
            self.current_page += 1
            await self.update_message(interaction)

    async def update_message(self, interaction: discord.Interaction):
        start = self.current_page * self.page_size
        end = start + self.page_size
        expressions_to_show = self.expressions[start:end]

        embed = discord.Embed(
            title="**Expressive** expression list",
            colour=embed_color,
            timestamp=datetime.now()
        )

        description_lines = [
            "**ID** | **Trigger** | **Action** | **Creator**"
        ]

        for exp in expressions_to_show:
            trigger = exp['trigger']
            if exp['trigger_type'] == "user":
                user = interaction.guild.get_member(int(trigger))
                trigger = user.name if user else trigger

            description_lines.append(
                f"{exp['id']} | {trigger} | {exp['action']} | {exp['created_by']}"
            )

        embed.description = "\n".join(description_lines)
        embed.set_footer(
            text=f"Showing {start + 1}-{min(end, len(self.expressions))} of {len(self.expressions)}",
            icon_url=icon_url
        )

        await interaction.response.edit_message(embed=embed, view=self)


def setup(bot):

    # /help

    @bot.tree.command(name="help", description="Show all available commands")
    async def help_command(interaction: discord.Interaction):
        embed = discord.Embed(
            title="**Expressive** help",
            description=(
                "**/help** - Show all available commands\n"
                "**/expression_new** - Create a new expression\n"
                "**/expression_guide** - Show a guide on how to make expressions\n"
                "**/expression_edit** - Edit an existing expression by ID\n"
                "**/expression_list** - Show a list of all expressions on the server\n"
                "**/expression_delete** - Delete an expression by ID"
            ),
            colour=embed_color,
            timestamp=datetime.now()
        )
        embed.set_footer(
            text=footer_text,
            icon_url=icon_url
        )
        await interaction.response.send_message(embed=embed)

    # /expression_new

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

        logger.info(f"Received expression_new command with trigger_type={trigger_type}, action={ \
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
    
    @bot.tree.command(name="expression_edit", description="Edit an existing expression by ID")
    @app_commands.describe(
        expression_id="The ID of the expression to edit",
        trigger_type="New trigger type: user or phrase",
        trigger="New user ID or phrase",
        action="New action",
        response="New message, URL, or emoji",
        cooldown="New cooldown in minutes"
    )
    async def expression_edit(
        interaction: discord.Interaction,
        expression_id: str,
        trigger_type: str = None,
        trigger: str = None,
        action: str = None,
        response: str = None,
        cooldown: int = None
    ):
        guild_id = str(interaction.guild.id)
        server_data = load_expressions(guild_id)
        expressions = server_data.get("expressions", [])

        expression_to_edit = next(
            (exp for exp in expressions if exp["id"] == expression_id), None)
        if not expression_to_edit:
            await interaction.response.send_message(f"No expression found with ID {expression_id}.", ephemeral=True)
            return

        if trigger_type:
            expression_to_edit["trigger_type"] = trigger_type.lower()
        if trigger:
            expression_to_edit["trigger"] = trigger
        if action:
            expression_to_edit["action"] = action.lower()
        if response:
            expression_to_edit["response"] = response
        if cooldown is not None:
            expression_to_edit["cooldown"] = cooldown

        save_expressions(guild_id, server_data)
        logger.info(f"Expression edited: {expression_to_edit}")
        await interaction.response.send_message(f"Expression with ID {expression_id} edited successfully.", ephemeral=True)

    @bot.tree.command(name="expression_guide", description="Show a guide on how to make expressions")
    async def expression_guide(interaction: discord.Interaction):
        embed = discord.Embed(title="Expression Guide",
                      description="Any problems creating an expression? This guide will help!",
                      colour=embed_color,
                      timestamp=datetime.now())
        embed.add_field(name="Using /expression_new",
                            value="This slash command will autofill all settable parameters for Expressions with options for all.",
                            inline=False)
        embed.add_field(name="Trigger Type - User / Phrase",
                            value="The parameter `trigger_type` will decide what will trigger this expression. **User** means that this expression will trigger when said user sends a message. **Phrase** means it will trigger when a set phrase is used.",
                            inline=False)
        embed.add_field(name="Trigger - UID / Phrase",
                            value="The parameter `trigger` will set the actual trigger for this expression. If `trigger_type` is set to **User**, input a user ID. If it's set to **Phrase**, input a custom phrase.",
                            inline=False)
        embed.add_field(name="Action - Send / Reply / React",
                            value="The parameter `action` will set what the bot will do in response to an expression being triggered. **Send** will send a message (without a reply). **Reply** will reply (with ping) to the message that triggered the expression. **React** will react with a set emote to the trigger.",
                            inline=False)
        embed.add_field(name="Response - Text / Emote",
                            value="The parameter `response` is a free field which allows you to set what the bot will respond with upon triggering the expression. If `action` is set to **React**, you __HAVE__ to input a single emoji that the bot has access to.",
                            inline=False)
        embed.add_field(name="Cooldown - Number",
                            value="The parameter `cooldown` sets how long until this expression can be triggered again. The unit is **Minutes**. Setting `cooldown` to **0** means there will be no cooldown, and the expression will trigger whenever possible. The same expression will **NOT** trigger multiple times on one message, regardless if the trigger phrase was used more than once. However, multiple expressions can trigger on one message.",
                            inline=False)
        embed.set_footer(
            text=footer_text,
            icon_url=icon_url
        )
                         


        await interaction.response.send_message(embed=embed)

    @bot.tree.command(name="expression_list", description="Show a list of all expressions on the server")
    async def expression_list(interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        server_data = load_expressions(guild_id)
        expressions = server_data.get("expressions", [])

        if not expressions:
            embed = discord.Embed(
                title="**Expressive** expression list",
                description="No expressions found for this server.",
                colour=embed_color,
                timestamp=datetime.now()
            )
            embed.set_footer(text=footer_text, icon_url=icon_url)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            paginator = Paginator(expressions)
            start = 0
            end = min(paginator.page_size, len(expressions))

            embed = discord.Embed(
                title="**Expressive** expression list",
                colour=embed_color,
                timestamp=datetime.now()
            )

            description_lines = [
                "**ID** | **Type** | **Response** | **Creator**"
            ]
            for exp in expressions[start:end]:
                trigger = exp['trigger']
                if exp['trigger_type'] == "user":
                    user = interaction.guild.get_member(int(trigger))
                    trigger = user.name if user else trigger

                description_lines.append(
                    f"{exp['id']} | {exp['trigger_type']} | {exp['response'] | exp['created_by']}"
                )

            embed.description = "\n".join(description_lines)
            embed.set_footer(
                text=f"Showing {start + 1}-{end} of {len(expressions)}",
                icon_url=icon_url
            )

            await interaction.response.send_message(embed=embed, view=paginator)

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
