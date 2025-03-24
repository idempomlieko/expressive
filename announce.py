import discord
import logging
import config
from discord.utils import get


icon = config.ICON_URL
logger = logging.getLogger(__name__)

async def send_intro_message(bot):
    changelog_lines = []
    try:
        with open("changelog.md", "r") as changelog_file:
            for line in changelog_file:
                if line.startswith("## "):
                    if changelog_lines:
                        break
                    changelog_lines.append(line.strip())
                elif line.startswith("- **") and changelog_lines:
                    changelog_lines.append(line.strip())
                elif line.strip() == "" and changelog_lines:  
                    break
    except FileNotFoundError:
        logger.error("changelog.md file not found.")
        changelog_lines = ["No changelog available."]

    if changelog_lines:
        version_title = changelog_lines[0].replace("## ", "") 
        changelog_content = "\n".join(changelog_lines[1:])
    else:
        version_title = "No Changelog Found"
        changelog_content = "No changelog available."

    embed = discord.Embed(
        title="Hello! I'm Expressive!",
        description="I'm a bot designed to enhance your Discord experience with custom expressions!",
        colour=0xc15bb2
    )
    embed.add_field(
        name="Some commands to get started:",
        value=(
            "**/help** - Show all available commands\n"
            "**/expression_new** - Create a new expression\n"
            "**/expression_guide** - Show a guide on how to make expressions"
        ),
        inline=False
    )
    embed.add_field(
        name=version_title,
        value=changelog_content,
        inline=False
    )
    embed.set_footer(text="Expressive | v0.3.0", icon_url=icon)

    for guild in bot.guilds:
        general_channel = get(guild.text_channels, name="general")
        if general_channel and general_channel.permissions_for(guild.me).send_messages:
            await general_channel.send(embed=embed)
        else:
            for channel in guild.text_channels:
                if channel.permissions_for(guild.me).send_messages:
                    await channel.send(embed=embed)
                    break