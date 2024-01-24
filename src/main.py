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

adminId = [422488203446976513, 301069013063172108, 409909528839192576]

client = commands.Bot(command_prefix = "!", case_insensitive = True, intents=discord.Intents.all())
builtins.client = client
builtins.debug = True

from helpers import *

lastSend = 0
nextSend = 0

def saveAteveryoneTime():
    try:
        with open('data.json', 'r') as f:
            data = json.load(f)
            data['lastSend'] = lastSend
            data['nextSend'] = nextSend
    except:
        data = {
            "lastSend": lastSend,
            "nextSend": nextSend
        }
    with open('data.json', 'w') as f:
        json.dump(data, f, indent=4)
    
    

def loadLastSend():
    global lastSend, nextSend
    try:
        with open('data.json', 'r') as f:
            data = json.load(f)
            lastSend = data['lastSend']
            nextSend = data['nextSend']
    except:
        lastSend = 0
        nextSend = 0
        saveAteveryoneTime()



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
import shop

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

@client.slash_command(guild=client.get_guild(guild))
async def dev(ctx, args:str):
    if (ctx.author.id not in adminId):
        return
    
    args = args.split(" ")
    logf(f"dev command from {ctx.author.name}: {args}")

    if (args[0] == "handouts"):
        money = int(args[1])
        await users.grantMoneyAll(money)

        await ctx.respond("done", ephemeral=True)
        if (len(args) == 2):
            return
        
        if (args[2] == "-a"):
            channel = client.get_channel(atEveryoneChannel)
            await channel.send(f"CHESTA STONE STIMULUS, EVERYONE GETS {money} CP @everyone ")

    elif(args[0] == "grabUsers"):
        await users.grabAllUsers()
        await ctx.respond("done", ephemeral=True)

    elif(args[0] == "grantPointsA"):
        points = int(args[1])
        await users.grantPointsAll(points)
        await ctx.respond(f"gave {points} to user", ephemeral=True)

    elif(args[0] == "setPointsA"):
        points = int(args[1])
        await users.setPointsAll(points)
        await ctx.respond("set points", ephemeral=True)

    elif(args[0] == "grantPoints"):
        user = client.get_user(int(args[1]))
        u = users.getUser(user.id)
        u.addPoints(int(args[2]))
        await ctx.respond(f"gave {args[2]} to user", ephemeral=True)

    elif(args[0] == "setPoints"):
        user = client.get_user(int(args[1]))
        u = users.getUser(user.id)
        u.setPoints(int(args[2]))
        await ctx.respond("set points", ephemeral=True)

    elif (args[0] == "fastforward"):
        h = int(args[1])
        m = int(args[2])
        s = int(args[3])
        fastForward(h, m, s)

        timeRemaining = nextSend - time.time()
        embed = discord.Embed(title="Next @everyone", description="The next @everyone will be sent at:", color=0x00ff00)
        embed.add_field(name="Time", value=f"`{formatTime(timeRemaining)}`", inline=True)
        embed.add_field(name="Time of day", value=f"`{datetime.datetime.fromtimestamp(nextSend).strftime('%I:%M %p')}`", inline=True)
        await ctx.respond(embed=embed, ephemeral=True)



    # get user arbitrary data
    elif(args[0] == "getUserArbData"):
        if (len(args) < 2):
            await ctx.respond("syntax is getUserArbData <userId> ?<key>", ephemeral=True)
            return
        
        user = client.get_user(int(args[1]))
        u = users.getUser(user.id)

        if (len(args) == 2):
            await ctx.respond(u.getArbitraryData(), ephemeral=True)
            return


        try:
            await ctx.respond(u.getArbitraryData(args[2]), ephemeral=True)
        except:
            await ctx.respond("failure", ephemeral=True)

    # set user arbitrary data
    elif(args[0] == "setUserArbData"):
        user = client.get_user(int(args[1]))
        u = users.getUser(user.id)
        u.addArbitraryData(args[2], args[3])
        await ctx.respond(f"set {args[2]} to {args[3]}", ephemeral=True)
    elif(args[0] == "help"):
        embed = discord.Embed(title="Dev Commands", description="The dev commands are:", color=0x00ff00)
        embed.add_field(name="handouts", value="`handouts <ammount> <announce>` - give everyone money", inline=False)
        embed.add_field(name="grabUsers", value="`grabUsers` - loads all users into the bot (DONT USE)", inline=False)
        embed.add_field(name="grantPointsA", value="`grantPointsA <ammount>` - give everyone points", inline=False)
        embed.add_field(name="setPointsA", value="`setPointsA <ammount>` - set everyones points", inline=False)
        embed.add_field(name="grantPoints", value="`grantPoints <userId> <ammount>` - give a user points", inline=False)
        embed.add_field(name="setPoints", value="`setPoints <userId> <ammount>` - set a users points", inline=False)
        embed.add_field(name="fastforward", value="`fastforward <hours> <minuites> <seconds>` - fast forwards time", inline=False)
        embed.add_field(name="getUserArbData", value="`getUserArbData <userId> ?<key>` - get a users arbitrary data", inline=False)
        embed.add_field(name="setUserArbData", value="`setUserArbData <userId> <key> <value>` - set a users arbitrary data", inline=False)
        embed.add_field(name="help", value="`help` - shows this message", inline=False)
        await ctx.respond(embed=embed, ephemeral=True)
    else:
        await ctx.respond("invalid command", ephemeral=True)


@client.slash_command(guild=client.get_guild(guild))
async def handouts(ctx, ammount:int, message:str = None):
    if (ctx.author.id not in adminId):
        return

    await users.grantMoneyAll(ammount)

    await ctx.respond("done", ephemeral=True)
    if (message == None):
        return
    
    channel = client.get_channel(atEveryoneChannel)
    await channel.send(message + f"({ammount} cp)")

    


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
    


@client.slash_command(guild=client.get_guild(guild))
async def getnext(ctx):
    embed = discord.Embed(title="Next @everyone", description="The next @everyone will be sent at:", color=0x00ff00)
    embed.add_field(name="Time", value=f"`{formatTime(nextSend - time.time())}`", inline=True)
    embed.add_field(name="Time of day", value=f"`{datetime.datetime.fromtimestamp(nextSend).strftime('%I:%M %p')}`", inline=True)
    await ctx.respond(embed=embed, ephemeral=True)


def getWaitTime():
    # gets how many seconds we need to wait untill 12pm the next day cst
    t = time.time()
    t = datetime.datetime.fromtimestamp(t)
    t = t.replace(hour=12, minute=0, second=0, microsecond=0)
    t = t.timestamp()
    if (t < time.time()):
        t += 86400
    return t - time.time()


if (builtins.debug):
    @client.slash_command(guild=client.get_guild(guild))
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

def fastForward(h, m, s):
    global lastSend, nextSend, usersLeft
    lastSend = time.time()
    nextSend -= h * 3600
    nextSend -= m * 60
    nextSend -= s
    saveAteveryoneTime()


usersLeft = 5
if (builtins.debug):
    @client.slash_command(guild_ids=[guild])
    async def fastforward(ctx, h:int, m:int, s:int):
        fastForward(h, m, s)
        await ctx.respond("done", ephemeral=True)

def getUserAtEveryoneTolerance(user : users.User):
    return 1800 + (user.dailyTime * 60)

@client.event
async def on_message(message):
    global usersLeft, lastSend, nextSend
    if message.author == client.user:
        return
    user = users.getUser(message.author.id)

    n = random.randint(0, 160)
    if n < 6 + user.onMessageChance:
        pts = 20 + user.onMsgPtsBonus
        users.grantPoints(message.author.id, pts)
        embed = discord.Embed(title="Points", description=f"+{pts} chesta points for `{message.author.name}`", color=0x00ff00)
        await message.channel.send(embed=embed)
        
        
    elif n == 34:
        n1 = random.randint(0, 200)
        if n1 < 20:
            embed = discord.Embed(title="THE RICHEST  IN THE WORLD", description=f"+500 chesta points for `{message.author.name}` @everyone", color=0x00ff00)
            await message.channel.send(embed=embed)
            users.grantPoints(message.author.id, 500 + user.onMsgPtsBonus)

    if (time.time() - lastSend >= getUserAtEveryoneTolerance(user)):
        usersLeft = 5
        # resets anyones streak if hasAtEveryoed is false

    
    # if the message contains @everyone
    if "@everyone" in message.content:
        # checks if its been more than 15 minuites since the last @everyone
        if (users.getUser(message.author.id).hasAtEveryoed == False):
            users.getUser(message.author.id).hasAtEveryoed = True
            #if its been 30 minuites since the last @everyone
            if (time.time() - lastSend >= getUserAtEveryoneTolerance(user)):
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

            user = users.getUser(message.author.id)

            try:
                streak = user.getArbitraryData("streak")
            except:
                streak = 0
                user.addArbitraryData("streak", 1)

            points += streak * 10
            user.addArbitraryData("streak", streak + 1)

            points += user.dailyBonus
            m = f"+{points} chesta points for `{message.author.name}`"

            if (streak > 0):
                m += f" (streak bonus: {streak * 10})"

            #usersLeft -= 1
            embed = discord.Embed(title="Points", description=m, color=0x00ff00)

            await message.channel.send(embed=embed)
            users.grantPoints(message.author.id, points)

    await client.process_application_commands(message)
    await client.process_commands(message)

@client.slash_command(guild_ids=[guild])
async def stats(ctx):
    user = users.getUser(ctx.author.id)
    embed = discord.Embed(title="Stats", description=f"Your stats are:", color=0x00ff00)
    embed.add_field(name="Points", value=f"`{user.points}`", inline=True)
    embed.add_field(name="@everyone pt bonus", value=f"`{user.dailyBonus}`", inline=True)
    embed.add_field(name="@everyone bonus time", value=f"`{user.dailyTime * 60}`", inline=True)
    embed.add_field(name="On Message Chance", value=f"`{user.onMessageChance + 5}%`", inline=True)
    embed.add_field(name="On Message Points", value=f"`{user.onMsgPtsBonus + 5}`", inline=True)
    embed.add_field(name="VC Hourly Rate", value=f"`{user.vcRewardsBonus + 30}`", inline=True)
    embed.add_field(name="VC Time", value=f"`{formatTime(user.getArbitraryData('vcTime'))}`", inline=True)
    try:
        pointsPDay = user.data['pointsPDay']
        embed.add_field(name="CP / day", value=f"`{pointsPDay}`", inline=True)
    except:
        pass
    await ctx.respond(embed=embed, ephemeral=True)

@client.slash_command(guild=client.get_guild(guild))
async def reload(ctx):
    if (ctx.author.id not in adminId):
        return
    return
    users.loadUserData()
    shop.reloadFromFiles()
    await ctx.respond("reloaded users, shop items", ephemeral=True)

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
    await shop.initialize()


def atExit():
    users.saveUserData()
    
    if nextSend != 0:
        saveAteveryoneTime()
        


if __name__ == "__main__":
    loadLastSend()
    atexit.register(atExit)
    client.run(token)

