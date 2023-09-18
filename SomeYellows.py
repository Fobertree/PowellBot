#Application ID: 1106017059168600134
#Public Key: e31a3157d7bd576a60f30086e0ee9851f68c9cfdb237c8def44be553c5b2d7bf
#Documentation: https://discordpy.readthedocs.io/en/stable/
#Guide: https://realpython.com/how-to-make-a-discord-bot-python/

#Used setx path command to set path for modules IIRC

import discord
import os
#import random
from dotenv import load_dotenv
from discord.ext import commands
latest_message_id = None
messageAuthor = ""

# Initializing Variables
load_dotenv()

intents = discord.Intents.all()
client = commands.Bot(command_prefix=".", intents=intents)
#print(os.getenv('DISCORD_TOKEN'))
token = os.getenv('DISCORD_TOKEN')

# Initializing our Bot
@client.event
async def on_ready():
    print("Logged in as a bot {0.user}".format(client))

# Bot Responses
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if isinstance(message.channel,discord.TextChannel):
        if message.channel.name == "popop":
            if message.content.startswith("hello".lower()) or message.content.startswith("hi".lower()):
                await message.channel.send("Hello {}!".format(message.author.name))
                await message.add_reaction('👋')
    if isinstance(message.channel,discord.DMChannel) or message.channel.name == "popop":
        if message.content.lower().startswith("poll"):
            messages = []
            timeout = 60
            await message.add_reaction('👍')
            await message.channel.send("You have started a poll.")
            await message.author.send("Enter your question: ")

            def check(m):
                return isinstance(m.channel, discord.DMChannel) and m.author == message.author

            try:
                question = await client.wait_for('message', check=check, timeout=60)
                messages.append(question.content)
                await message.author.send("Question received: {}".format(question.content))

                # Continue processing the poll or implement additional logic here
                # You can use the `messages` list to track the message IDs
                while timeout > 0:
                    answer = await client.wait_for('message')
                    messages.append(answer.content)
                    await message.author.send("Answer received: {}".format(answer.content))
                    if answer.content=="done":
                        await message.author.send("Sending poll now.")
                        answers = set(messages[1:len(messages)-1])
                        channel = discord.utils.get(client.get_all_channels(),name = "popop")
                        poll = "Question: {}\nAnswer(s): {}".format(str(messages[0]), ', '.join(list(answers)))
                        #print(poll)
                        await message.channel.send(poll) #can add emoji dict

            except TimeoutError:
                if len(messages) == 1:
                    await message.author.send("Question timed out. Poll creation cancelled.")
                else:
                    message.popOPchannel.send("Poll complete.")


client.run(token)
