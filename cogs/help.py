import discord
from discord.ext import commands
from discord import Intents
from dotenv import load_dotenv
from discord.ui import View,Select
# https://pypi.org/project/discord.py-pagination/

intents = Intents.all()
bot = commands.Bot(command_prefix =".",intents=intents)

class HelpSelect(Select):
    print("Initializing help dropdown")
    def __init__(self,bot: commands.Bot):
        super().__init__(
            placeholder="Choose a category",
            options = [
                discord.SelectOption(
                label=cog_name,description=cog.__doc__
                ) for cog_name, cog in bot.cogs.items()
            ]
        )
        self.bot = bot
    
    async def callback(self,interaction: discord.Interaction) -> None:
        cog = self.bot.get_cog(self.values[0])
        assert cog

        commands_mixer = []
        for i in cog.walk_commands():
            commands_mixer.append(i)
        
        for i in cog.walk_app_commands():
            commands_mixer.append(i)
        
        embed = discord.Embed(
            title=f'{cog.__cog_name__} Commands',
            description = '\n'.join(f'\n**{command.name}**: `{command.description}`' for command in commands_mixer)
        )

        await interaction.response.send_message(embed=embed,ephemeral=True)

class help(commands.Cog):
    def __init__(self,bot):
        self.bot=bot
    
    @commands.hybrid_command(name='help',description ='Shows list of commands')
    async def help_command(self,ctx: commands.Context):
        embed = discord.Embed(title = 'Help command',description=("Get help commands"),color=(discord.Color.blue()))

        view = View().add_item(HelpSelect(self.bot))
        await ctx.send(embed=embed,view=view)

    @commands.command(name = "ID",description="Get your own ID. Used for testing/development purposes")
    async def id(self,ctx):
        await ctx.send(ctx.message.author.id)

async def setup(bot):
    print("Setting up help")
    await bot.add_cog(help(bot))

setup(bot)

# Pagination