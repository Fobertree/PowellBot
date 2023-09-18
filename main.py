# https://gist.github.com/AbstractUmbra/a9c188797ae194e592efe05fa129c57f
import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
import asyncio

import logging
import logging.handlers

discord.utils.setup_logging(level=logging.INFO,root=False)


load_dotenv()

intents = discord.Intents.all()
intents.message_content = True

#bot = commands.Bot(command_prefix='.', intents=intents,description="Making Alex question life decisions")
#tree = discord.app_commands.CommandTree(bot)
token = os.getenv('DISCORD_TOKEN')
owner = os.getenv('OWNER_ID')

active_cogs = set()

class Bot(commands.Bot):
    def __init__(self,intents: discord.Intents,**kwargs):
        super().__init__(command_prefix=commands.when_mentioned_or('.'),intents=intents,description="Making Alex question life decisions",**kwargs)

bot = Bot(intents=intents,help_command=None)

async def load_extensions():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            if filename.startswith('llm'):
                continue
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                active_cogs.add(f'cogs.{filename[:-3]}')
            except Exception as e:
                print(f"Failed importing cog {filename[:-3]}. {e}")

# Initializing our Bot
@bot.event
async def on_ready():
    activity = discord.Game("Actively Inting Fobert",type=3)
    await bot.change_presence(status=discord.Status.online,activity = activity)
    await load_extensions()

    print(active_cogs)
    print("Logged in as a bot {0.user}".format(bot))

@bot.tree.command(name = 'hello')
@app_commands.describe(member="The member you want me to say hi to.")
async def hello(interaction,member: discord.Member):
    await interaction.response.send_message(f'Hello {member}')

@bot.tree.command(name='sync', description='Owner only') #manually sync
async def sync(interaction: discord.Interaction):
    print(type(owner),type(interaction.user.id))
    if interaction.user.id == int(owner):
        synced = await bot.tree.sync()
        response = f'Command tree synced. {synced}, Number synced: {len(synced)}'
        print(response)
        #await interaction.response.send_message(response)
    else:
        await interaction.response.send_message('You must be the owner to use this command!')

@bot.command()
async def test(ctx,arg):
    embed = discord.Embed(description=(f"{arg} Test"),colour=discord.Colour.purple())
    await ctx.send(embed=embed)
@bot.command()
async def ping(ctx):
    await ctx.send("Pong")

bot.run(token)
