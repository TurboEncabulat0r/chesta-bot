import discord, asyncio
from discord.ext import commands
import random, json, os, builtins
from helpers import * 
import users
guild = builtins.guild
client = builtins.client

"""
shop where users can buy items, items go to thier inventory
thier inventory is stored as arbetryary data in the user object
items may have a action that can be triggered by events
the actions will be stored as a string in the item object
items are stored in itemPath in individual json files

commands:
    shop ?<item> - shows the shop or a specific item, if none given shows a list of all
    buy <item> ?<number> - buys an item from the shop
    sell <item> ?<number> - sells an item to the shop
    inventory - shows the users inventory
    additem <name> <desc> <price> <qty> <image> - adds an item to the shop
    removeitem <name> - removes an item from the shop
    stock <item> <qty> - changes the stock of an item

actions:
generatePtsPerDay
 - data {"pts": n}
increaseOnMessageChance
    - data {"chance": n}
increaseOnMessagePts
    - data {"pts": n}
increaseDailyBonus
    - data {"bonus": n}
increaseVcRewards
    - data {"bonus": n}
increaseDailyTime
    - data {"time": n}
"""


# data may contain anything or nothing, example uses are if we have an item that generates pts every day
# we can have a data field that stores the number of pts it generates
exampleAction = {"name": "example",
                 "data": {}}

itemPath = "shopitems"

class Item():
    def __init__(self, name, desc, price, qty, action, imageLink, alias, owner):
        self.name = name
        self.desc = desc
        self.price = price
        self.qty = qty
        self.action = action
        self.imageLink = imageLink
        self.owner = owner
        self.alias = alias

    def __str__(self):
        return f"**{self.name}** : `{self.price}`"

    def __repr__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, Item):
            return self.name == other.name
        return False
    
    def checkAlias(self, name):
        for a in self.alias:
            if a.lower() == name.lower():
                return True
        return False
    
    def toDict(self):
        return {
            "name": self.name,
            "desc": self.desc,
            "price": self.price,
            "qty": self.qty,
            "imageLink": self.imageLink,
            "action": self.action,
            "owner": self.owner,
            "alias": self.alias
            
        }
    
    def payOwner(self):
        if self.owner != 0:
            users.getUser(self.owner).addPoints(self.price)
            logf(f"paid {self.owner} ${self.price} for {self.name}")

    def refund(self, user):
        # removes from owner and gives to user
        if self.owner != 0:
            users.getUser(self.owner).removePoints(self.price)
            user.addPoints(self.price)
            logf(f"refunded {self.owner} ${self.price} for {self.name}")
            self.owner = user.id
        else:
            user.addPoints(self.price)
            logf(f"refunded ${self.price} for {self.name}")
        
    
    def toUserItem(self):
        return {
            "name": self.name,
            "qty": 1,
            "action": self.action
        }
    
    def toEmbed(self):
        embed = discord.Embed(title=self.name, description=self.desc)
        embed.add_field(name="Price", value=self.price)
        embed.add_field(name="Stock", value=self.qty)
        embed.set_image(url=self.imageLink)
        return embed
    
items = []

def getItem(name):
    for item in items:
        if item.name.lower() == name.lower() or item.checkAlias(name):
            return item
    return None

def loadItems():
    global items
    items = []
    num = 0
    for filename in os.listdir(itemPath):
        with open(itemPath + "/" + filename, "r") as f:
            item = Item(**json.load(f))
            items.append(item)
            num += 1
    logf(f"loaded {num} items")



def saveItems():
    for item in items:
        with open(itemPath + "/" + item.name + ".json", "w") as f:
            json.dump(item.toDict(), f, indent=4)


def saveItemByName(name):
    item = getItem(name)
    if item != None:
        with open(itemPath + "/" + item.name + ".json", "w") as f:
            json.dump(item.toDict(), f, indent=4)


# adds pts per day to the users arbiterary data
async def addPtsPerDay(user : users.User, pts):
    if "ptsPerDay" in user.data:
        user.data["ptsPerDay"] += pts
    else:
        user.data["ptsPerDay"] = pts

async def ptsPerDayTask():
    while True:
        total = 0
        for user in users.users:
            if "ptsPerDay" in user.data:
                user.addPoints(user.data["ptsPerDay"])
                total += user.data["ptsPerDay"]

        logf(f"added {total} pts to users for daily bonus")
        await asyncio.sleep(60 * 60 * 24)

def getUserInventory(user):
    inv = None
    try:
        inv = user.getArbitraryData("inventory")
    except Exception as e:
        user.addArbitraryData("inventory", [])
        inv = user.getArbitraryData("inventory")
    return inv

def addItemToInventory(user, item):
    # if the user has the item in thier inventory, increase the qty
    inv = getUserInventory(user)
    for i in inv:
        if i["name"] == item.name:
            i["qty"] += 1
            break
    else:
        inv.append(item.toUserItem())
        
    
    user.setArbitrayData("inventory", inv)

def removeItemFromInventory(user, item):
    inv = getUserInventory(user)
    for i in inv:
        if i["name"] == item.name:
            i["qty"] -= 1
            if i["qty"] <= 0:
                inv.remove(i)
                
            break
    user.setArbitrayData("inventory", inv)

        
        


# loops through thier inventory and returns a dict of thier bonuses
def getUserBonusus(user : users.User):
    bonuses = {"onMessageChance": 0,
               "onMessagePts": 0,
               "dailyBonus": 0,
               "vcRewards": 0,
               "dailyTime": 0}
    
    inv = getUserInventory(user)
    # loops through all items in the users inventory and adds thier bonuses to the dict
    for item in inv:
        try:
            if item["action"]["name"] == "increaseOnMessageChance":
                bonuses["onMessageChance"] += item["action"]["data"]["chance"]
            elif item["action"]["name"] == "increaseOnMessagePts":
                bonuses["onMessagePts"] += item["action"]["data"]["pts"]
            elif item["action"]["name"] == "increaseDailyBonus":
                bonuses["dailyBonus"] += item["action"]["data"]["bonus"]
            elif item["action"]["name"] == "increaseVcRewards":
                bonuses["vcRewards"] += item["action"]["data"]["bonus"]
            elif item["action"]["name"] == "increaseDailyTime":
                bonuses["dailyTime"] += item["action"]["data"]["time"]
        except:
            pass
    


    return bonuses

def initializeUsers():
    for user in users.users:
        user.setBonusValues(getUserBonusus(user))

    logf("set user shop item item bonuses")


def addPtsPerDay(user : users.User, pts):
    if "ptsPerDay" in user.data:
        user.data["ptsPerDay"] += pts
    else:
        user.data["ptsPerDay"] = pts


@client.slash_command(guild_ids=[guild])
async def shop(ctx, item_name:str=None):
    if item_name == None:
        embed = discord.Embed(title="Shop", description="The shop has the following items:", color=0x00ff00)
        for item in items:
            embed.add_field(name=item.name, value=f"**${item.price}**", inline=False)
        await ctx.respond(embed=embed, ephemeral=True)
    else:
        item = getItem(item_name)
        if item == None:
            await ctx.respond("Item not found", ephemeral=True)
        else:
            await ctx.respond(embed=item.toEmbed(), ephemeral=True)



# adds the item to the users inventory, and applies any actions
def buyItem(user, item, qty):
    user.removePoints(item.price * qty)
    for i in range(qty):
        addItemToInventory(user, item)
    try:
        if item.action["name"] == "generatePtsPerDay":
            addPtsPerDay(user, item.action["data"]["pts"] * qty)
    except:
        pass
    user.setBonusValues(getUserBonusus(user))
    item.payOwner()

def sellItem(user, item, qty):
    user.addPoints(item.price * qty)
    for i in range(qty):
        removeItemFromInventory(user, item)
    user.setBonusValues(getUserBonusus(user))
    item.payOwner()

@client.slash_command(guild_ids=[guild])
async def buy(ctx, item_name:str, qty:int=1):
    item = getItem(item_name)
    if item == None:
        embed = discord.Embed(title="Shop", description=f"Item `{item_name}` not found", color=0x00ff00)
        await ctx.respond(embed=embed)
    else:
        if item.qty < qty and item.qty != -1:
            embed = discord.Embed(title="Shop", description="Not enough stock", color=0x00ff00)
            await ctx.respond(embed=embed, ephemeral=True)
        elif users.getUser(ctx.author.id).points < item.price * qty:
            embed = discord.Embed(title="Shop", description=f"Not enough points for **{item_name}** (${item.price * qty})", color=0x00ff00)
            await ctx.respond(embed=embed, ephemeral=True)
        else:
            buyItem(users.getUser(ctx.author.id), item, qty)
            if item.qty != -1:
                item.qty -= qty
            saveItemByName(item.name)
            embed = discord.Embed(title="Shop", description=f"GMFD! {qty}x**{item.name}** bought for `{item.price * qty}`", color=0x00ff00)
            await ctx.respond(embed=embed, ephemeral=True)


@client.slash_command(guild_ids=[guild])
async def sell(ctx, item_name:str, qty:int=1):
    item = getItem(item_name)
    if item == None:
        embed = discord.Embed(title="Shop", description=f"Item `{item_name}` not found", color=0x00ff00)
        await ctx.respond(embed=embed)
    else:
        if qty > 0:
            sellItem(users.getUser(ctx.author.id), item, qty)
            if item.qty != -1:
                item.qty += qty
            saveItemByName(item.name)
            embed = discord.Embed(title="Shop", description=f"GMFD! {qty}x**{item.name}** sold for `{item.price * qty}`", color=0x00ff00)
            await ctx.respond(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(title="Shop", description=f"Invalid qty", color=0x00ff00)
            await ctx.respond(embed=embed, ephemeral=True)


@client.slash_command(guild_ids=[guild])
async def inventory(ctx, user:discord.User=None):
    if user == None:
        user = users.getUser(ctx.author.id)
    else:
        user = users.getUser(user.id)

    embed = discord.Embed(title="Inventory", description=f"**{user.name}**'s inventory")

    inv = getUserInventory(user)
    for item in inv:
        embed.add_field(name=item["name"], value=f"**{item['qty']}**", inline=False)
    await ctx.respond(embed=embed, ephemeral=True)

@client.slash_command(guild_ids=[guild])
async def additem(ctx, name:str, desc:str, price:int, qty:int, alias:str, image:str):
    if getItem(name) != None:
        await ctx.respond("item already exists", ephemeral=True)
        return

    item = Item(name, desc, price, qty, {}, image, alias.split(","), ctx.author.id)
    items.append(item)
    saveItems()
    embed = discord.Embed(title="Shop", description=f"Item `{name}` added", color=0x00ff00)
    await ctx.respond(embed=embed, ephemeral=True)

@client.slash_command(guild_ids=[guild])
async def removeitem(ctx, name:str):
    item = getItem(name)
    if item == None:
        await ctx.respond("item not found", ephemeral=True)
    else:
        items.remove(item)
        saveItems()
        await ctx.respond("item removed", ephemeral=True)
    
async def initialize():
    initializeUsers()
    asyncio.create_task(ptsPerDayTask())


loadItems()


