# Expressive | A Discord chat reactions bot!
### Current Version - v0.3.0

Expressive is a simple discord bot utilising discords discord.py library for bot and application development.
For this to properly work, you will need to set up a discord application via the Discord Dev Portal - guide below.

Read the changelog for a deeper look into the development of Expressive!

## Features
- **Custom reactions** - create Expressions which allow you to create custom reactions and interactions. Select if the Expression triggers on phrase or user message; if the bot sends a message, replies or reacts, and what the contents of this message will be!

## Work in progress 
- **Welcome messages** - a feature which, while already in Discord by default, will bring a little spark. Create a custom message with embeds to welcome new users.
- **Anti-harassment measures** - will allow users to opt out of these features, along with letting administrators set blacklists for people who can't create presets, banned words, minimum times...
- **Bot updates** - will allow you to keep in touch with the development of Expressive and stay updated as soon as a new update rolls out.
- **Community server**

## Planned features
- **Reaction roles**
- **Moderation capabilities**
- **Compound Expressions**


## Command list
- **help** - shows all commands
- **expression_guide** - shows a guide on Expressions
- **expression_new** - creates new Expression
- **expression_list** - shows all Expressions in the server
- **expression_delete** - deletes an Expression
- **expression_edit** - edits an Expression
- **expression_info** - information about an Expression
- **expression_role** - sets who can manage Expressions
- **expression_logs** - logs Expression management 

### Setting up a Discord bot:
1. In [Discord Developer Portal](https://discord.com/developers/applications), create a new application with a custom name.
2. Navigate to the **OAuth2** tab on the left. Scroll down to **OAuth2 URL Generator**. In **Scopes** , select **bot** and **applications.commands**. Under **Permissions**, either select *Admin*, or manually pick permissions you deem fit. For this one, I picked *View Channels, Send Messages, Send Messages in Threads, Manage Messages, Embed Links, Attach Files, Read Message History, Use External Emojis, Use External Stickers, Add Reactions*.
3.  Under **Integration Type**, select **Guild install**. Copy the link and save it - you will use it to invite the bot to your servers.
4.  Navigate to the **Bot** tab on the left. There, get your app's **Client Secret (token)** and save it in a secure place. **Do NOT share this token.** Scroll down to *Privileged Gateway Intents* and enable **Message Content Intent** (the last one).


### Installation steps:
1. Clone / download the contents of the repository.
2. Create a virtual environment.
3. Navigate to the installation folder and run `pip install -r requirements.txt` - This will install all libraries used.
4. Create the **config.py** and add the following: `TOKEN = 'YOUR TOKEN HERE' ` (including the apostrophe).
5. Run the bot by navigating into your installation folder and running:  Linux / MacOS :  `python3 bot.py`  Windows : `python bot.py` 
