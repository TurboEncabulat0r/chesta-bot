import discord, asyncio
from discord.ext import commands
import random, json, os, builtins

guild = builtins.guild
client = builtins.client

class StockBase():
    def __init__(self, name, v, startingShares, pps):
        self.name = name
        self.volitility = v
        self.shares = startingShares
        self.pricePerShare = pps

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
            "pricePerShare": self.pricePerShare
        }
        
    def sellStocks(self, shares):
        money = shares * self.pricePerShare
        self.shares -= shares
        return money

    def getPrice(self):
        return self.pricePerShare
    
def loadFromFiles():
    path = "stocks/"

    #iterate through the files in the stocks folder
    stocks = []
    for file in os.listdir(path):
        if (file.endswith(".json")):
            with open(path + file, "r") as f:
                data = json.load(f)
                stocks.append()
