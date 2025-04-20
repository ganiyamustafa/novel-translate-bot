import os
import discord
import asyncio

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.event
async def on_ready():
  print(f'{bot.user.name} has connected to Discord! ${bot.guilds}')


async def load():
  for filename in os.listdir("./cogs"):
    if filename.endswith("py"):
      await bot.load_extension(f"cogs.{filename[:-3]}")

async def main():
  async with bot:
    await load()
    await bot.start(TOKEN)

asyncio.run(main())