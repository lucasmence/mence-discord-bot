import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
PREFIXO = os.getenv('PREFIX', '!') 

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIXO, intents=intents)

async def load_extensions():
    print("--- Carregando Módulos ---")
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f'✅ {filename} carregado com sucesso.')
            except Exception as e:
                print(f'❌ Erro ao carregar {filename}: {e}')
    print("--------------------------")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot desligado.")