import discord, asyncio
from discord.ext import commands
import random, json, os, builtins
import users

guild = builtins.guild
client = builtins.client

"""
commands:
    stocks - list all stocks
    stocks buy - buy a stock
    stocks sell - sell a stock
    stocks info - get info on a stock
"""

class StockBase():
    def __init__(self, name, v, startingShares, pps):
        self.name = name
        self.volitility = v
        self.shares = startingShares
        self.pricePerShare = pps
        self.icon = None
        self.iconPath = ""

        self.history = []

    async def simulate(self):
        while True:
            self.pricePerShare += random.uniform(-self.volitility, self.volitility)
            await asyncio.sleep(random.randint(60, 160))

    def _affectStockPrice(self, amount):
        # ammount is the number of shares, we will use this to calculate how much the price should change
        if (amount > 0):
            self.pricePerShare += ((amount * self.volitility) * 0.4) * random.uniform(0, 1)
        else:
            self.pricePerShare += ((amount * self.volitility) * 0.4) * random.uniform(-1, 0)

    def buyStocks(self, ammount):
        self.shares += ammount
        money = ammount * self.pricePerShare
        return money

    def tojson(self):
        return {
            "name": self.name,
            "volitility": self.volitility,
            "shares": self.shares,
            "pricePerShare": self.pricePerShare,
            "history": self.history,
            "icon": self.iconPath 
        }
        
    def sellStocks(self, shares):
        money = shares * self.pricePerShare
        self.shares -= shares
        return money

    def getPrice(self):
        return self.pricePerShare
    
stocks = []

async def buy(user, stock, n):
    pass

async def sell(user, stock, n):
    pass

async def info(uset, stock):
    pass

async def display(page):
    pass

    
@client.slash_command(guild_ids=[guild])
async def stocks(ctx, args:str):
    args = args.split(" ")
    user = users.getUser(ctx.author.id)
    if (args[0] == "buy"):
        if (len(args) < 3):
            await ctx.respond("You need to specify a stock and an ammount", ephemeral=True)
            return
        stock = args[1]
        ammount = int(args[2])
        await buy(stock, ammount)
    elif (args[0] == "sell"):
        if (len(args) < 3):
            await ctx.respond("You need to specify a stock and an ammount", ephemeral=True)
            return
        stock = args[1]
        ammount = int(args[2])
        await sell(stock, ammount)
    elif (args[0] == "info"):
        if (len(args) < 2):
            await ctx.respond("You need to specify a stock", ephemeral=True)
            return
        stock = args[1]
    else:
        try:
            if int(args[0]) > 0 and int(args[0]) < len(stocks/3):
                await display(int(args[0]))
                return
        except:
            pass


    
def loadFromFiles():
    path = "stocks/"

    #iterate through the files in the stocks folder
    stocks = []
    for file in os.listdir(path):
        if (file.endswith(".json")):
            with open(path + file, "r") as f:
                data = json.load(f)
                stocks.append()

    return stocks
