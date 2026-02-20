import discord
from discord.ext import commands
import os
import re

token = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Success: {bot.user}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    instagramRegex = r"(https?://(?:www\.)?instagram\.com/(?:p|reels|reel)/([^/?#&]+))"
    match = re.search(instagramRegex, message.content)

    if match:
        linkDefault = match.group(1)
        linkNew = linkDefault.replace("instagram.com", "kkinstagram.com")
            
        try:
            await message.delete()
        except discord.Forbidden:
            return

        content = f"[{message.author.display_name}]({linkNew})"
            
        await message.channel.send(content)

    twitterRegex = r"(https?://(?:www\.)?(?:twitter\.com|x\.com)/[a-zA-Z0-9_]+/status/[0-9]+)"
    match = re.search(twitterRegex, message.content)

    if match:
        linkDefault = match.group(1)
        linkNew = linkDefault.replace("x.com", "fxtwitter.com")
            
        try:
            await message.delete()
        except discord.Forbidden:
            return

        content = f"[{message.author.display_name}]({linkNew})"
            
        await message.channel.send(content)

    await bot.process_commands(message)

if token:
    bot.run(token)
else:
    print("Error: DISCORD_TOKEN not found!")
