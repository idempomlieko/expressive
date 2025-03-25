import asyncio
import config
import discord
import logging
import random
import re
import string

from discord import app_commands
from discord.ui import View, Button, Select
from datetime import datetime

from file_handling import load_expressions, save_expressions

logger = logging.getLogger(__name__)

icon = config.ICON_URL
embed_color = 0xc15bb2
footer_text = "Expressive"

def setup(bot):
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
                "**/expression_delete** - Delete an expression by ID\n"
                "**/expression_info** - Show detailed information about an expression by ID\n"
                "**/expression_role** - Set who can manage expressions\n"
                "**/expression_logs** - Configure logging for Expressions"
            ),
            colour=embed_color,
            timestamp=datetime.now()
        )
        embed.set_footer(
            text=footer_text,
            icon_url=icon
        )
        await interaction.response.send_message(embed=embed)


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

        #logger.info(f"Received expression_new command with trigger_type={trigger_type}, action={ \
                    #action}, trigger={trigger}, response={response}, cooldown={cooldown}")

        if trigger_type == "user":
            match = re.match(r"<@!?(\d+)>", trigger)
            if match:
                user_id = match.group(1)
            elif trigger.isdigit():
                user_id = trigger
            else:
                user = discord.utils.get(interaction.guild.members, name=trigger)
                if not user:
                    await interaction.response.send_message("User not found!", ephemeral=True)
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
        # logger.info(f"Expression added: {expression}")
        log_message = (
            f"**New Expression Created**\n"
            f"**ID:** {expression_id}\n"
            f"**Creator:** {interaction.user}\n"
            f"**Trigger Type:** {trigger_type}\n"
            f"**Action:** {action}"
        )
        await send_log(interaction, "log_create", log_message)
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
        #logger.info(f"Expression edited: {expression_to_edit}")
        changes = []
        if trigger_type:
            changes.append(f"Trigger Type: {expression_to_edit['trigger_type']} -> {trigger_type.lower()}")
            expression_to_edit["trigger_type"] = trigger_type.lower()
        if trigger:
            changes.append(f"Trigger: {expression_to_edit['trigger']} -> {trigger}")
            expression_to_edit["trigger"] = trigger
        if action:
            changes.append(f"Action: {expression_to_edit['action']} -> {action.lower()}")
            expression_to_edit["action"] = action.lower()
        if response:
            changes.append(f"Response: {expression_to_edit['response']} -> {response}")
            expression_to_edit["response"] = response
        if cooldown is not None:
            changes.append(f"Cooldown: {expression_to_edit['cooldown']} -> {cooldown}")
            expression_to_edit["cooldown"] = cooldown
        save_expressions(guild_id, server_data)
        log_message = (
            f"**Expression Edited**\n"
            f"**ID:** {expression_id}\n"
            f"**Editor:** {interaction.user}\n"
            f"**Changes:**\n" + "\n".join(changes)
        )
        await send_log(interaction, "log_edit", log_message)
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
            icon_url=icon
        )
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
            # logger.info(f"Expression deleted: {expression_to_delete}")
            log_message = (
            f"**Expression Deleted**\n"
            f"**ID:** {expression_id}\n"
            )
            await send_log(interaction, "log_create", log_message)
            await interaction.response.send_message(f"Expression with ID {expression_id} deleted successfully.", ephemeral=True)
        else:
            await interaction.response.send_message(f"No expression found with ID {expression_id}.", ephemeral=True)

    @bot.tree.command(name="expression_info", description="Show detailed information about an expression by ID")
    @app_commands.describe(expression_id="The ID of the expression to display")
    async def expression_info(interaction: discord.Interaction, expression_id: str):
        guild_id = str(interaction.guild.id)
        server_data = load_expressions(guild_id)
        expressions = server_data.get("expressions", [])

        expression = next((exp for exp in expressions if exp["id"] == expression_id), None)

        if expression:
            trigger = expression["trigger"]
            if expression["trigger_type"] == "user":
                trigger = f"<@{trigger}>"

            embed = discord.Embed(
                title=f"Expression Details - {expression['id']}",
                colour=embed_color,
                timestamp=datetime.now()
            )
            embed.add_field(name="Trigger Type", value=expression["trigger_type"], inline=True)
            embed.add_field(name="Trigger", value=trigger, inline=True)
            embed.add_field(name="Action", value=expression["action"], inline=True)
            embed.add_field(name="Response", value=expression["response"], inline=True)
            embed.add_field(name="Cooldown", value=f"{expression['cooldown']} minutes", inline=True)
            embed.add_field(name="Created By", value=expression["created_by"], inline=True)
            embed.set_footer(text=footer_text, icon_url=icon)

            await interaction.response.send_message(embed=embed, ephemeral=False)
        else:
            await interaction.response.send_message(f"No expression found with ID {expression_id}.", ephemeral=False)

    class ExpressionListView(View):
        def __init__(self, interaction, expressions, page=0):
            super().__init__(timeout=None)
            self.interaction = interaction
            self.expressions = expressions
            self.page = page
            self.update_view()

        def update_view(self):
            self.clear_items()
            start = self.page * 10
            end = start + 10
            current_expressions = self.expressions[start:end]

            select = Select(placeholder="Select an expression by ID", min_values=1, max_values=1)
            for exp in current_expressions:
                select.add_option(label=exp["id"], value=exp["id"])
            select.callback = self.select_callback
            self.add_item(select)

            if self.page > 0:
                left_button = Button(label="⬅️", style=discord.ButtonStyle.primary)
                left_button.callback = self.left_callback
                self.add_item(left_button)

            if end < len(self.expressions):
                right_button = Button(label="➡️", style=discord.ButtonStyle.primary)
                right_button.callback = self.right_callback
                self.add_item(right_button)

        def create_embed(self):
            start = self.page * 10
            end = min(start + 10, len(self.expressions))
            current_expressions = self.expressions[start:end]

            embed = discord.Embed(
                title="Expression List",
                colour=embed_color,
                timestamp=datetime.now()
            )

            expression_lines = []
            for exp in current_expressions:
                truncated_response = (exp["response"][:10] + "...") if len(exp["response"]) > 10 else exp["response"]
                expression_lines.append(f"{exp['id']} | {exp['trigger_type']} | {truncated_response} | {exp['created_by']}")

            embed.add_field(
                name="ID | Type | Response | Creator",
                value="\n".join(expression_lines),
                inline=False
            )

            embed.set_footer(
                text=f"Showing {start + 1}-{end}/{len(self.expressions)}",
                icon_url=icon
            )
            return embed

        async def select_callback(self, interaction: discord.Interaction):
            selected_id = interaction.data["values"][0]
            expression = next((exp for exp in self.expressions if exp["id"] == selected_id), None)
            if expression:
                trigger = expression["trigger"]
                if expression["trigger_type"] == "user":
                    trigger = f"<@{trigger}>"

                embed = discord.Embed(
                    title=f"Expression Details - {expression['id']}",
                    colour=embed_color,
                    timestamp=datetime.now()
                )
                embed.add_field(name="Trigger Type", value=expression["trigger_type"], inline=True)
                embed.add_field(name="Trigger", value=trigger, inline=True)
                embed.add_field(name="Action", value=expression["action"], inline=True)
                embed.add_field(name="Response", value=expression["response"], inline=True)
                embed.add_field(name="Cooldown", value=f"{expression['cooldown']} minutes", inline=True)
                embed.add_field(name="Created By", value=expression["created_by"], inline=True)
                embed.set_footer(text=footer_text, icon_url=icon)

                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message("Expression not found.", ephemeral=True)

        async def left_callback(self, interaction: discord.Interaction):
            self.page -= 1
            self.update_view()
            embed = self.create_embed()
            await interaction.response.edit_message(embed=embed, view=self)

        async def right_callback(self, interaction: discord.Interaction):
            self.page += 1
            self.update_view()
            embed = self.create_embed()
            await interaction.response.edit_message(embed=embed, view=self)


    @bot.tree.command(name="expression_list", description="Show a list of all expressions on the server")
    async def expression_list(interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        server_data = load_expressions(guild_id)
        expressions = server_data.get("expressions", [])

        if not expressions:
            await interaction.response.send_message("No expressions found on this server.", ephemeral=False)
            return

        view = ExpressionListView(interaction, expressions)
        embed = view.create_embed()
        await interaction.response.send_message(embed=embed, view=view, ephemeral=False)


    @bot.tree.command(name="expression_role", description="Set who can manage expressions (Admins, Everyone, or a specific role)")
    async def expression_role(interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You do not have permission to use this command.", ephemeral=False)
            return

        guild_id = str(interaction.guild.id)
        server_data = load_expressions(guild_id)

        expression_perms = server_data["info"].get("expression_perms", {"type": "admin", "role_id": None})

        if expression_perms["type"] == "admin":
            current_setting = "Admins only"
        elif expression_perms["type"] == "everyone":
            current_setting = "Everyone"
        elif expression_perms["type"] == "role" and expression_perms["role_id"]:
            role_obj = interaction.guild.get_role(expression_perms["role_id"])
            current_setting = f"@{role_obj.name}" if role_obj else "Unknown Role"
        else:
            current_setting = "Admins only"

        embed = discord.Embed(
            title="Expression Role Settings",
            description=f"Currently set to: **{current_setting}**\n\n"
                        "1️⃣ **Admins only**\n"
                        "2️⃣ **Everyone**\n"
                        "3️⃣ **Tag Role**",
            colour=embed_color,
            timestamp=datetime.now()
        )
        embed.set_footer(text=footer_text, icon_url=icon)

        view = ExpressionRoleView(interaction, server_data)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=False)

# ----------------------------------------------------------------- /EXPRESSION_LOGS

    @bot.tree.command(name="expression_logs", description="Configure logging for Expressions")
    async def expression_logs(interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("You don't have permission to use this.", ephemeral=True)
            return

        guild_id = str(interaction.guild.id)
        server_data = load_expressions(guild_id)
        if "expression_logs" not in server_data["info"]:
            server_data["info"]["expression_logs"] = {
                "channel_id": None,
                "log_create": True,
                "log_edit": True,
                "log_delete": True,
                "log_trigger": True
            }

        await interaction.response.send_message(
            embed=make_logs_embed(server_data),
            view=ExpressionLogsView(interaction, server_data),
            ephemeral=False
        )
    
    class ExpressionRoleView(View):
        def __init__(self, interaction: discord.Interaction, server_data):
            super().__init__(timeout=60)
            self.interaction = interaction
            self.server_data = server_data

        async def on_timeout(self):
            pass

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.user != self.interaction.user:
                await interaction.response.send_message("You cannot interact with this menu.", ephemeral=True)
                return False
            return True

        @discord.ui.button(label="Admins only", style=discord.ButtonStyle.primary)
        async def admin_button(self, interaction: discord.Interaction, button: Button):
            self.server_data["info"]["expression_perms"] = {"type": "admin", "role_id": None}
            save_expressions(str(interaction.guild.id), self.server_data)
            await self.update_embed(interaction, "Admins only")

        @discord.ui.button(label="Everyone", style=discord.ButtonStyle.primary)
        async def everyone_button(self, interaction: discord.Interaction, button: Button):
            self.server_data["info"]["expression_perms"] = {"type": "everyone", "role_id": None}
            save_expressions(str(interaction.guild.id), self.server_data)
            await self.update_embed(interaction, "Everyone")

        @discord.ui.button(label="Tag Role", style=discord.ButtonStyle.primary)
        async def role_button(self, interaction: discord.Interaction, button: Button):
            await interaction.response.send_message("Please tag a role to set permissions.", ephemeral=False)

            def check(message):
                return (
                    message.author == interaction.user
                    and message.channel == interaction.channel
                    and len(message.role_mentions) > 0
                )

            try:
                message = await interaction.client.wait_for("message", check=check, timeout=30)
                role = message.role_mentions[0]
                self.server_data["info"]["expression_perms"] = {"type": "role", "role_id": role.id}
                save_expressions(str(interaction.guild.id), self.server_data)
                await message.reply(f"Expression permissions set to @{role.name}.", ephemeral=False)
            except asyncio.TimeoutError:
                await interaction.followup.send("You took too long to respond. Please try again.", ephemeral=True)

        async def update_embed(self, interaction: discord.Interaction, new_setting: str):
            embed = discord.Embed(
                title="Expression Role Settings",
                description=f"Currently set to: **{new_setting}**\n\n"
                            "1️⃣ **Admins only**\n"
                            "2️⃣ **Everyone**\n"
                            "3️⃣ **Tag Role**",
                colour=embed_color,
                timestamp=datetime.now()
            )
            embed.set_footer(text=footer_text, icon_url=icon)
            await interaction.response.edit_message(embed=embed, view=self)


    def make_logs_embed(server_data):
        logs = server_data["info"].get("expression_logs", {})
        current_channel = "None" if not logs.get("channel_id") else f"<#{logs['channel_id']}>"
        lines = [
            f"Set which channel and what to log regarding Expressions.",
            f"**Current log channel:** {current_channel}",
            "",
            f"**➕ Created New Expression:** {'ON ✅' if logs['log_create'] else 'OFF ❌'}",
            f"**📝 Edited Expression:** {'ON ✅' if logs['log_edit'] else 'OFF ❌'}",
            f"**🚫 Deleted Expression:** {'ON ✅' if logs['log_delete'] else 'OFF ❌'}",
            # f"**‼️ Expression Triggered:** {'ON ✅' if logs['log_trigger'] else 'OFF ❌'}",    # CURRENTLY DOESNT WORK!!!!
            "",
            "Use the buttons below to toggle each option or set a new channel."
        ]

        embed = discord.Embed(
            title="Expression Logs Settings",
            description="\n".join(lines),
            colour=embed_color,
            timestamp=datetime.now()
        )
        embed.set_footer(text=footer_text, icon_url=icon)
        return embed


    async def send_log(interaction: discord.Interaction, log_type: str, log_message: str):
        guild_id = str(interaction.guild.id)
        server_data = load_expressions(guild_id)
        logs = server_data["info"].get("expression_logs", {})
        channel_id = logs.get("channel_id")

        if not logs.get(log_type, False):
            return

        if channel_id:
            channel = interaction.guild.get_channel(channel_id)
            if channel:
                embed = discord.Embed(
                    title="Expression Log",
                    description=log_message,
                    colour=embed_color,
                    timestamp=datetime.now()
                )
                embed.set_footer(text=footer_text, icon_url=icon)
                await channel.send(embed=embed)


    class ExpressionLogsView(View):
        def __init__(self, interaction: discord.Interaction, server_data):
            super().__init__(timeout=60)
            self.interaction = interaction
            self.server_data = server_data

        async def on_timeout(self):
            pass

        async def interaction_check(self, interaction: discord.Interaction) -> bool:
            if interaction.user != self.interaction.user:
                await interaction.response.send_message("You cannot use this.", ephemeral=True)
                return False
            return True
        
        async def update_message(self, interaction: discord.Interaction):
            await interaction.response.edit_message(embed=make_logs_embed(self.server_data), view=self)

        @discord.ui.button(label="➕", style=discord.ButtonStyle.primary)
        async def toggle_create(self, interaction: discord.Interaction, button: Button):
            logs = self.server_data["info"]["expression_logs"]
            logs["log_create"] = not logs["log_create"]
            save_expressions(str(interaction.guild.id), self.server_data)
            await self.update_message(interaction)

        @discord.ui.button(label="📝", style=discord.ButtonStyle.primary)
        async def toggle_edit(self, interaction: discord.Interaction, button: Button):
            logs = self.server_data["info"]["expression_logs"]
            logs["log_edit"] = not logs["log_edit"]
            save_expressions(str(interaction.guild.id), self.server_data)
            await self.update_message(interaction)

        @discord.ui.button(label="🚫", style=discord.ButtonStyle.primary)
        async def toggle_delete(self, interaction: discord.Interaction, button: Button):
            logs = self.server_data["info"]["expression_logs"]
            logs["log_delete"] = not logs["log_delete"]
            save_expressions(str(interaction.guild.id), self.server_data)
            await self.update_message(interaction)

        """@discord.ui.button(label="‼️", style=discord.ButtonStyle.primary)
        async def toggle_trigger(self, interaction: discord.Interaction, button: Button):
            logs = self.server_data["info"]["expression_logs"]
            logs["log_trigger"] = not logs["log_trigger"]
            save_expressions(str(interaction.guild.id), self.server_data)
            await self.update_message(interaction)"""
        ## CURRENTLY DOESNT WORK!!!!

        @discord.ui.button(label="Change Channel", style=discord.ButtonStyle.secondary)
        async def change_channel(self, interaction: discord.Interaction, button: Button):
            await interaction.response.send_message("Tag the new logs channel:", ephemeral=False)

            def check(msg):
                return (
                    msg.author == interaction.user
                    and msg.channel == interaction.channel
                    and len(msg.channel_mentions) > 0
                )

            try:
                msg = await interaction.client.wait_for("message", check=check, timeout=30)
                channel_id = msg.channel_mentions[0].id
                self.server_data["info"]["expression_logs"]["channel_id"] = channel_id
                save_expressions(str(interaction.guild.id), self.server_data)
                await interaction.followup.send(f"Expression logs channel set to <#{channel_id}>.", ephemeral=False)
            except asyncio.TimeoutError:
                await interaction.followup.send("You took too long to respond. Please try again.", ephemeral=True)

        
    