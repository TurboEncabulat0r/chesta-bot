import discord, asyncio
from discord.ext import commands
import random, json, os, builtins
from helpers import * 

guild = builtins.guild
client = builtins.client

users = []

class User():
    def __init__(self, id):
        self.id = id

        try:
            self.name = client.get_user(id).name
        except:
            self.name = "Unknown"

        self.points = 0
        self.hasAtEveryoed = False
        self.onMessageChance = 0
        self.onMsgPtsBonus = 0
        self.dailyBonus = 0
        self.vcRewardsBonus = 0
        self.rawJson = None
        self.data = {}
    
    def addArbitraryData(self, key, value):
        # if it already exists, update it
        if key in self.data:
            self.data[key] = value
            return
        d = {key : value}
        self.data.update(d)

    def setArbitrayData(self, key, value):
        self.addArbitraryData(key, value)

    def getArbitraryData(self, key= None):
        if (key == None):
            return self.data
        return self.data[key]
    
    def removeArbitraryData(self, key):
        if key in self.data:
            self.data.pop(key)
    
    async def send(self, message):
        try:
            await client.get_user(self.id).send(message)
        except:
            pass

    def addPoints(self, points):
        self.points += points

    def removePoints(self, points):
        self.points -= points

        
    def setBonusValues(self, d):
        self.onMessageChance = d["onMessageChance"]
        self.onMsgPtsBonus = d["onMessagePts"]
        self.dailyBonus = d["dailyBonus"]
        self.vcRewardsBonus = d["vcRewards"]
        self.dailyTime = d["dailyTime"]
        

    def initFromJson(self, json):
        self.points = json['points']
        self.id = json['id']
        self.name = client.get_user(self.id).name
        try:
            self.data = json['data']
        except:
            pass
        self.rawJson = json


    def tojson(self):
        
        return {
            "name": self.name,
            "id": self.id,
            "points": self.points,
            "data": self.data
        }

def loadUserData():
    global users
    num = 0
    tmp = []
    with open('users.json') as f:
        for u in json.load(f):
            u = dict(u)
            usr = User(u['id'])
            usr.initFromJson(u)
            tmp.append(usr)
            num += 1 

    # sanitize
    temp2 = tmp
    for user in tmp:
        if user.name == "Unknown":
            tmp.remove(user)
        
        for user2 in temp2:
            if user.id == user2.id and user != user2:
                tmp.remove(user2)
                logf("removed duplicate user " + user2.name)

    users = tmp
    logf(f"loaded {num} users")

async def grabAllUsers():
    # registers all the users in the guild
    global users
    g = client.get_guild(guild)
    for user in g.members:
        if not userInList(user.id):
            registerUser(user.id)

async def grantMoneyAll(pts, dm=False):
    global users
    for user in users:
        user.addPoints(pts)
        if (dm):
            pass
            #await dmUser(user.id, "You have been given 10 chesta points", False)

    saveUserData()

def saveUserData():
    logf("saving user data")
    if (len(users) == 0):
        return
    
    with open('users.json', 'w') as f:
        data = []
        for user in users:
            data.append(user.tojson())
        json.dump(data, f, indent=4)


def userInList(id):
    for user in users:
        if user.id == id:
            return True
    return False

def getUser(id):
    for user in users:
        if user.id == id:
            return user
        
    return registerUser(id)

def registerUser(id):
    logf("registering user " + client.get_user(id).name)
    if not userInList(id):
        u = User(id)
        users.append(u)
        saveUserData()
        return u
    
def grantPoints(id, points):
    if userInList(id):
        getUser(id).addPoints(points)
    else:
        registerUser(id).addPoints(points)

    saveUserData()

@client.slash_command(guild_ids=[guild])
async def pay(ctx, user:discord.User, ammount:int):
    if userInList(ctx.author.id):
        if (ctx.author.id == user.id):
            embed = discord.Embed(title="Points", description=f"You can't pay yourself", color=0x00ff00)
            await ctx.respond(embed=embed, ephemeral=True)
            return
        
        if (ammount <= 0):
            embed = discord.Embed(title="Points", description=f"You can't pay negative chesta points", color=0x00ff00)
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if getUser(ctx.author.id).points >= ammount:
            
            getUser(ctx.author.id).removePoints(ammount)
            grantPoints(user.id, ammount)
            embed = discord.Embed(title="Points", description=f"Sent `{ammount}` chesta points to `{user.name}`", color=0x00ff00)
            await ctx.respond(embed=embed, ephemeral=True)
            await dmUser(user.id, f"You have been sent `{ammount}` chesta points from `{ctx.author.name}` ni||ce ca||r")
        else:
            embed = discord.Embed(title="Points", description=f"You don't have enough chesta points", color=0x00ff00)
            await ctx.respond(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(title="Points", description=f"You don't have enough chesta points", color=0x00ff00)
        await ctx.respond(embed=embed, ephemeral=True)

def resetAtEveryone():
    global users
    for user in users:
        user.hasAtEveryoed = False

@client.slash_command(guild_ids=[guild])
async def getpoints(ctx, user: discord.Member = None):
    if user == None:
        user = ctx.author
    if userInList(user.id):
        embed = discord.Embed(title="Points", description=f"`{user.name}` has `{getUser(user.id).points}` points", color=0x00ff00)
        await ctx.respond(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(title="Points", description=f"`{user.name}` has `0` points", color=0x00ff00)
        await ctx.respond(embed=embed, ephemeral=True)


@client.slash_command(guild_ids=[guild])
async def top(ctx):
    embed = discord.Embed(title="Top", description="Top 5 chesta points", color=0x00ff00)
    # returns a soted list of users by points
    l = []
    sortedUsers = []
    for i in users:
        l.append({"id": i.id, "points": i.points})


    #sorts the list by points
    for i in range(len(l)):
        max = l[0]
        for j in l:
            if j['points'] > max['points']:
                max = j
        sortedUsers.append(getUser(max['id']))
        l.remove(max)

    for i in range(5):
        if (i >= len(sortedUsers)):
            break
        embed.add_field(name=f"{i+1}. {sortedUsers[i].name}", value=f"`{sortedUsers[i].points}`", inline=False)
    await ctx.respond(embed=embed, ephemeral=True)

if (builtins.debug):
    @client.slash_command(guild_ids=[guild])
    async def setpoints(ctx, user : discord.Member, points:int):


        getUser(user.id).points = points
        saveUserData()
        embed = discord.Embed(title="Points", description=f"`{user.name}` now has `{points}` points", color=0x00ff00)
        await ctx.respond(embed=embed, ephemeral=True)
