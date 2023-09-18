import discord
from discord.ext import commands
from discord import Intents
from pydoc import importfile
import os
import importlib.util

'''llm_path = r"LLM\DollyLLM.py"
if os.path.exists(llm_path):
    print("True")
else:
    print("False")

from pathlib import Path
import sys

sys.path.append(str(llm_path))
print(sys.path)

spec = importlib.util.spec_from_file_location("DollyLLM",llm_path)
DollyLLM = importlib.util.module_from_spec(spec)
spec.loader.exec_module(DollyLLM)'''

# https://huggingface.co/databricks/dolly-v2-3b
# pip install "accelerate>=0.16.0,<1" "transformers[torch]>=4.28.1,<5" "torch>=1.13.1,<2"

import torch
from transformers import pipeline

generate_text = pipeline(model="databricks/dolly-v2-3b", torch_dtype=torch.bfloat16, trust_remote_code=True, device_map="auto")

def prompt(input):
    res = generate_text(str(input))
    return (res[0]["generated_text"])


intents = Intents.all()
bot = commands.Bot(command_prefix =".",intents=intents)

class llm(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @commands.command()
    async def gpt(self,ctx,arg):
        print(arg)
        result = prompt(arg)
        print(result)
        await ctx.send(result)

async def setup(bot):
    print("setting up LLM")
    await bot.add_cog(llm(bot))

setup(bot)