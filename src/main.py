import discord, json, requests, atexit
from discord.ext import commands
import asyncio, random
import time
import builtins
import datetime

# config vars
token = ""
userId = 0
guild = 0
inactiveRole = 0
atEveryoneChannel = 0
offlineTimeout = 10

adminId = [422488203446976513]

client = commands.Bot(command_prefix = "!", case_insensitive = True, intents=discord.Intents.all())
builtins.client = client
builtins.debug = True

from helpers import *

lastSend = 0
nextSend = 0

try:
    # Load config
    with open('config.json') as f:
        config = json.load(f)
        token = config['token']
        userId = config['userId']
        guild = config['guild']
        builtins.debug = config['debug']
        inactiveRole = config['inactiveRole']
        offlineTimeout = config['offlineTimeout']
        atEveryoneChannel = config['atEveryoneChannel']
except:
    logf("Error loading config.json, rewriting defaults", "w")
    with open('config.json', 'w') as f:
        config = {
            "token": token,
            "userId": userId,
            "guild": guild,
            "debug": builtins.debug,
            "inactiveRole": inactiveRole,
            "offlineTimeout": offlineTimeout,
            "atEveryoneChannel": atEveryoneChannel
        }
        json.dump(config, f, indent=4)



builtins.guild = guild
import users

# import all modules here
#import stocks
import gambling
import vcimpl

async def watchForUserUpdate():
    # checks every 10 seconds if the user is offline, if so applies the inactive role
    if (userId == 0):
        return
    u = client.get_user(userId)
    member = client.get_guild(guild).get_member(userId)
    lastStatus = member.status
    while True:
        if member.status == discord.Status.offline and lastStatus != discord.Status.offline:
            
            await member.add_roles(discord.Object(id=inactiveRole))
            logf("applied inactive role to " + u.name)
        lastStatus = member.status
        await asyncio.sleep(offlineTimeout)

@client.slash_command(guild_ids=[guild])
async def dev(ctx, args:str):
    if (ctx.author.id != adminId[0]):
        return
    
    args = args.split(" ")

    if (args[0] == "handouts"):
        money = int(args[1])
        await users.grantMoneyAll(money)

        await ctx.respond("done", ephemeral=True)
        if (len(args) == 2):
            return
        
        if (args[2] == "-a"):
            channel = client.get_channel(atEveryoneChannel)
            await channel.send(f"CHESTA STONE STIMULUS, EVERYONE GETS {money} CP @everyone ")

    if(args[0] == "grabUsers"):
        await users.grabAllUsers()
        await ctx.respond("done", ephemeral=True)
        


@client.slash_command(guild=client.get_guild(guild))
async def activate(ctx, pswd:int):
    # if user does not have inactive role give it to them, if they do take it away
    if (ctx.author.id != userId):
        return

    if pswd == 1984:
        
        if inactiveRole in [role.id for role in ctx.author.roles]:
            await ctx.author.remove_roles(discord.Object(id=inactiveRole))
            logf("deactivated " + ctx.author.name)
        else:
            await ctx.author.add_roles(discord.Object(id=inactiveRole))
            logf("activated " + ctx.author.name)
    else:
        logf("wrong password from " + ctx.author.name)
    


@client.slash_command(guild_ids=[guild])
async def getnext(ctx):
    embed = discord.Embed(title="Next @everyone", description="The next @everyone will be sent at:", color=0x00ff00)
    embed.add_field(name="Time", value=f"`{formatTime(nextSend - time.time())}`", inline=True)
    embed.add_field(name="Time of day", value=f"`{datetime.datetime.fromtimestamp(nextSend).strftime('%I:%M %p')}`", inline=True)
    await ctx.respond(embed=embed, ephemeral=True)


def getWaitTime():
    # gets the seconds till midnight tonight
    # then takes a random number between 10 and 20
    # then multiplies that by the number of seconds in a day
    # the goal is to have the time @everyone is sent to be a random time between 10am and 12pm
    timeTillMidnight = (datetime.datetime.combine(datetime.date.today(), datetime.time.max) - datetime.datetime.now()).total_seconds()
    hours = random.uniform(10, 22)
    return (hours * 3600) + timeTillMidnight

if (builtins.debug):
    @client.slash_command(guild_ids=[guild])
    async def recalctime(ctx):
        global nextSend
        nextSend = getWaitTime() + time.time()
        embed = discord.Embed(title="Next @everyone", description="The next @everyone will be sent at:", color=0x00ff00)
        embed.add_field(name="Time", value=f"`{formatTime(nextSend - time.time())}`", inline=True)
        embed.add_field(name="Time of day", value=f"`{datetime.datetime.fromtimestamp(nextSend).strftime('%I:%M %p')}`", inline=True)
        await ctx.respond(embed=embed, ephemeral=True)


async def ScheduleTimedAtEveryone():
    global lastSend, nextSend
    while True:
        if (time.time() >= nextSend):
            channel = client.get_channel(atEveryoneChannel)
            await channel.send("DAILY @everyone")
            lastSend = time.time()
            nextSend = getWaitTime() + lastSend
            saveAteveryoneTime()
            users.resetAtEveryone()
            logf("sent @everyone")
        await asyncio.sleep(5)


usersLeft = 5
if (builtins.debug):
    @client.slash_command(guild_ids=[guild])
    async def fastforward(ctx, h:int, m:int, s:int):
        global lastSend, nextSend, usersLeft
        lastSend = time.time()
        nextSend -= h * 3600
        nextSend -= m * 60
        nextSend -= s
        saveAteveryoneTime()
        usersLeft = 5
        users.resetAtEveryone()
        await ctx.respond("fast forwarded", ephemeral=True)
    

@client.event
async def on_message(message):
    global usersLeft, lastSend, nextSend
    if message.author == client.user:
        return
        
    n = random.randint(0, 100)
    if n < 5:
        users.grantPoints(message.author.id, 5)
        embed = discord.Embed(title="Points", description=f"+5 chesta points for `{message.author.name}`", color=0x00ff00)
        await message.channel.send(embed=embed)
        
        
    elif n == 34:
        n = random.randint(0, 100)
        if n == 34:
            embed = discord.Embed(title="THE RICHEST  IN THE WORLD", description=f"+500 chesta points for `{message.author.name}` @everyone", color=0x00ff00)
            await message.channel.send(embed=embed)
            users.grantPoints(message.author.id, 500)

    if (time.time() - lastSend >= 1800):
        usersLeft = 5
    
    # if the message contains @everyone
    if "@everyone" in message.content:
        # checks if its been more than 15 minuites since the last @everyone
        if (users.getUser(message.author.id).hasAtEveryoed == False):
            users.getUser(message.author.id).hasAtEveryoed = True
            #if its been 30 minuites since the last @everyone
            if (time.time() - lastSend >= 1800):
                usersLeft = 5
                return
            
            if (usersLeft <= 0):
                return
            
            points = 0
            if (usersLeft == 5):
                points = 100
            elif (usersLeft == 4):
                points = 75
            elif (usersLeft == 3):
                points = 50
            elif (usersLeft == 2):
                points = 25
            elif (usersLeft == 1):
                points = 10
            usersLeft -= 1
            embed = discord.Embed(title="Points", description=f"+{points} chesta points for `{message.author.name}`", color=0x00ff00)

            await message.channel.send(embed=embed)
            users.grantPoints(message.author.id, points)

    await client.process_application_commands(message)
    await client.process_commands(message)


@client.event
async def on_ready():
    logf("Bot ready")

    logf(f"""  Client Information
 > user: '{client.user}' intiialized
 > monitoring user: '{client.get_user(userId)}'
 > servers: '{client.guilds[0].name}'""")
    
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="god motherfuckin damnnn"))

    users.loadUserData()
    asyncio.create_task(watchForUserUpdate())
    asyncio.create_task(ScheduleTimedAtEveryone())
    asyncio.create_task(vcimpl.vcScanner())


def atExit():
    users.saveUserData()
    
    if nextSend != 0:
        saveAteveryoneTime()
        
def saveAteveryoneTime():
    logf("saving data")
    with open('data.json', 'w') as f:
        j = {
            "lastSend": lastSend,
            "nextSend": nextSend
        }
        json.dump(j, f, indent=4)
        f.close()


def loadLastSend():
    global lastSend, nextSend
    try:
        with open('data.json') as f:
            j = json.load(f)
            lastSend = j['lastSend']
            nextSend = j['nextSend']
            logf("lastSend loaded: " + str(lastSend))
            f.close()
    except:
        saveAteveryoneTime()

if __name__ == "__main__":
    loadLastSend()
    atexit.register(atExit)
    client.run(token)

