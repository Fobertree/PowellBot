import discord
from discord.ext import commands
from discord import Intents, Interaction
import asyncio
import yfinance as yf
import matplotlib # embed pyplot chart
import pandas as pd
from discord import app_commands
import importlib.util
import sys

spec = importlib.util.spec_from_file_location('database','database.py')
database = importlib.util.module_from_spec(spec)
sys.modules['database'] = database
spec.loader.exec_module(database)
#database.MyClass()

database_funcs = {}

create_user = database.create_user
buy_stock = database.buy_stock
get_user_stocks = database.get_user_stocks
sell_stock = database.sell_stock
reset = database.reset
get_money = database.get_money
plot_history = database.plot_history
stocks_to_table = database.stocks_to_table
get_portfolio_history = database.get_portfolio_history
default_money = database.default_money

intents = Intents.all()
bot = commands.Bot(command_prefix =".",intents=intents)



class finance(commands.Cog,commands.Bot):
    def __init__(self,bot: commands.Bot):
        self.bot: commands.Bot = bot

    @commands.hybrid_command(name='ticker',description='Get the most recent price for a ticker')
    @app_commands.describe(ticker = "Stock ticker")
    async def ticker(self,ctx,ticker):
        stock = yf.Ticker(ticker)
        #print(stock.history(period="1d"))
        #print(stock.info)
        await ctx.send(f'{ticker.upper()} price is {(pd.to_numeric(stock.history(period = "1day")["Close"],errors = "coerce").values[0]):.2f}')
    
    @commands.hybrid_command(name='create',description="Create an account")
    async def create(self,ctx):
        await ctx.send(ctx.message.author.name)
        await ctx.send(create_user(ctx.message.author.id,default_money))

    @commands.hybrid_command(name='buy',description='Buy a stock')
    @app_commands.describe(tkr = "Stock ticker", shares = "Number of shares")
    async def buy(self,ctx,tkr,shares):
        print(tkr,shares,type(tkr),type(shares))
        print(ctx.message.author.id)
        response = buy_stock(ctx.message.author.id,tkr,shares)
        await ctx.send(response)
    @buy.error
    async def check_ticker(self,ctx,error):
        if isinstance(error,commands.CommandInvokeError):
            if isinstance(error.__cause__,IndexError):
                await ctx.send("Invalid ticker.")
                return
            await ctx.send(type(error.__cause__))

    @commands.hybrid_command(name='sell',description='Sell a stock')
    @app_commands.describe(tkr= "Stock ticker", shares = "Number of shares")
    async def sell(self,ctx,tkr,shares):
        await ctx.defer()
        response = sell_stock(ctx.message.author.id,tkr,shares)
        await ctx.send(response)

    @commands.hybrid_command(name='portfolio',description="Get your stock holdings")
    async def portfolio(self,ctx,tkr=None):
        await ctx.defer()
        response = stocks_to_table(ctx.message.author.id)
        get_portfolio_history(ctx.message.author.id)
        file = discord.File('test.png')
        if response:
            embed = discord.Embed(title = f"**{ctx.message.author.name.upper()}**", description=f"\n```{response}```",colour=discord.Colour.yellow())
            embed.set_image(url="attachment://test.png")
        else:
            embed = discord.Embed(description=(f"Hello {ctx.message.author.name}, you have no stocks."))
        
        await ctx.send(embed=embed,file = file)

    @commands.command(title = "reset",description = "Owner only command")
    async def reset(self,ctx,id):
        if int(ctx.message.author.id) == 433764142999011350:
            reset(id,default_money)
            await ctx.send("Done.")
        else:
            await ctx.send("You do not have permission to use this command.")

    @commands.hybrid_command(title = "Cash",description = "Check how much purely liquid cold, hard, cash you have")
    async def check(self,ctx):
        response = get_money(ctx.message.author.id)
        await ctx.send(f'{response:.2f}')


async def setup(bot):
    print("setting up FINANCE")
    print(f'Default money: {default_money}')
    await bot.add_cog(finance(bot))

setup(bot)