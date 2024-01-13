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

client = commands.Bot(command_prefix = "!", case_insensitive = True, intents=discord.Intents.all())
builtins.client = client
builtins.debug = True

users = []

class Bet():
    def __init__(self, challanegr, challangee, ammount):
        self.challanger = challanegr
        self.challangee = challangee
        self.ammount = ammount
        self.accepted = False


class User():
    def __init__(self, id):
        self.id = id

        try:
            self.name = client.get_user(id).name
        except:
            self.name = "Unknown"

        self.points = 0
        self.hasAtEveryoed = False
        self.bets = []

    def appendBet(self, bet):
        logf(f"appending bet {bet.challanger.name} -> {bet.challangee.name}")
        self.bets.append(bet)
        print(len(self.bets))

    def getNextBet(self):
        print(self.bets.challanegr.name)
        next = self.bets[0]
        self.bets.remove(next)
        return next
    
    def hasAccepted(self, bet:Bet):
        for i in self.bets:
            if i == bet:
                return bet.accepted



    def addPoints(self, points):
        self.points += points

    def removePoints(self, points):
        self.points -= points

    def initFromJson(self, json):
        self.points = json['points']
        self.id = json['id']
        self.name = client.get_user(self.id).name

    def tojson(self):
        return {
            "id": self.id,
            "points": self.points
        }

def loadUserData():
    num = 0
    with open('users.json') as f:
        for u in json.load(f):
            u = dict(u)
            usr = User(u['id'])
            usr.initFromJson(u)
            users.append(usr)
            num += 1 

    logf(f"loaded {num} users")

def saveUserData():
    logf("saving user data")
    with open('users.json', 'w') as f:
        json.dump([user.tojson() for user in users], f, indent=4)

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

savedLogs = []
firstLog = False
def logf(str, args = None):
    if (not firstLog):
        with open("log.txt", "w") as f:
            f.write("---- New Log Session ----\n")
            f.close()
    msg = ""
    t = f"[{time.strftime('%H:%M:%S')}] "
    if (args == "e"):
        msg = f"{t}[ERROR] {str}"
    elif (args == "w"):
        msg = f"{t}[WARNING] {str}"
    elif (args == "i"):
        msg = f"{t}[INFO] {str}"
    elif (args == "d"):
        msg = f"{t}[DEBUG] {str}"
    else:
        msg = f"{t}[INFO] {str}"

    print(msg)
    savedLogs.append(msg)

# private vars
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

# import all modules here
#import stocks
#import gambling


def formatTime(seconds, internal=False):
    if internal:
            hours = int(seconds // 3600)
            seconds -= hours * 3600
            minutes = int(seconds // 60)
            seconds -= minutes * 60
            return [hours, minutes, seconds]
    hours = int(seconds // 3600)
    seconds -= hours * 3600
    minutes = int(seconds // 60)
    seconds -= minutes * 60
    return f"{hours} hours, {minutes} minutes, {seconds} seconds"


async def watchForUserUpdate():
    # checks every 10 seconds if the user is offline, if so applies the inactive role
    u = client.get_user(userId)
    member = client.get_guild(guild).get_member(userId)
    lastStatus = member.status
    while True:
        if member.status == discord.Status.offline and lastStatus != discord.Status.offline:
            
            await member.add_roles(discord.Object(id=inactiveRole))
            logf("applied inactive role to " + u.name)
        lastStatus = member.status
        await asyncio.sleep(offlineTimeout)


async def dmUser(id, message, embed=False):
    user = client.get_user(id)
    if embed:
        await user.send(embed=message)
    else:
        await user.send(message)

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


def resetAtEveryone():
    for user in users:
        user.hasAtEveryoed = False


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

async def scheduleTimedMessage(channel, timeRange, message, times=-1):
    global lastSend, nextSend
    if (times == -1):
        while True:
            if lastSend <= 40:
                lastSend = time.time()
                wtime = getWaitTime()
                nextSend = wtime + time.time()
                saveAteveryoneTime()
                resetAtEveryone()
                await channel.send(message)
                logf("sending again in " + str(wtime / 60) + " minuites")
                await asyncio.sleep(wtime)

            else:
                # uses the time since the last @everyone to calculate the next @everyone
                seconds = getWaitTime()
                logf("sending again in " + str(seconds) + " seconds")
                
                await asyncio.sleep(seconds)
                lastSend = time.time()
                nextSend = getWaitTime() + time.time()
                saveAteveryoneTime()
                resetAtEveryone()
                await channel.send(message)


            


    else:
        for i in range(times):
            await channel.send(message)
            await asyncio.sleep(hours * 3600)

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
    async def invoke(ctx):

        global lastSend, nextSend
        resetAtEveryone()
        logf("invoked @everyone", 'i')
        channel = client.get_channel(atEveryoneChannel)
        await channel.send("DAILY @everyone")
        lastSend = time.time()
        nextSend = getWaitTime() + lastSend
        saveAteveryoneTime()

if (builtins.debug):
    @client.slash_command(guild_ids=[guild])
    async def setpoints(ctx, user : discord.Member, points:int):


        getUser(user.id).points = points
        saveUserData()
        embed = discord.Embed(title="Points", description=f"`{user.name}` now has `{points}` points", color=0x00ff00)
        await ctx.respond(embed=embed, ephemeral=True)

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
    
usersLeft = 5
@client.event
async def on_message(message):
    global usersLeft, lastSend, nextSend
    if message.author == client.user:
        return
        
    n = random.randint(0, 100)
    if n < 5:
        grantPoints(message.author.id, 5)
        embed = discord.Embed(title="Points", description=f"+5 chesta points for `{message.author.name}`", color=0x00ff00)
        await message.channel.send(embed=embed)
        
        
    elif n == 34:
        n = random.randint(0, 100)
        if n == 34:
            embed = discord.Embed(title="THE RICHEST  IN THE WORLD", description=f"+500 chesta points for `{message.author.name}` @everyone", color=0x00ff00)
            await message.channel.send(embed=embed)
            grantPoints(message.author.id, 500)
    
    
    # if the message contains @everyone
    if "@everyone" in message.content:
        # checks if its been more than 15 minuites since the last @everyone
        if (getUser(message.author.id).hasAtEveryoed == False):
            if (not builtins.debug):
                getUser(message.author.id).hasAtEveryoed = True
            
            #if its been 30 minuites since the last @everyone
            if (time.time() - lastSend > 1800):
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
            grantPoints(message.author.id, points)

    await client.process_application_commands(message)
    await client.process_commands(message)


@client.slash_command(guild_ids=[guild])
async def acceptbet(ctx):
    user = getUser(ctx.author.id)

    if user.bets != []:
        bet = user.getNextBet()
        bet.accepted = True
        embed = discord.Embed(title="Bet", description=f"You have accepted the bet", color=0x00ff00)
        await ctx.respond(embed=embed, ephemeral=True)


    else:
        print(user.bets)
        print(user.name)
        print(user.bets == [])
        print(type(user.bets))
        print(len(user.bets))
        embed = discord.Embed(title="Bet", description=f"You have no bets to accept", color=0x00ff00)
        await ctx.respond(embed=embed, ephemeral=True)


async def awaitBetResponse(bet):
    embed = discord.Embed(title="Bet Challange", description=f"You have been challenged to a bet.", color=0x00ff00)
    embed.add_field(name="Challenger", value=f"`{bet.challanger.name}`", inline=True)
    embed.add_field(name="Ammount", value=f"`{bet.ammount}`", inline=True)
    embed.add_field(name="Accept", value=f"Accept the bet by running `/acceptbet` in the server", inline=False)

    await dmUser(bet.challangee.id, embed, True)
    getUser(bet.challanger.id).appendBet(bet)

    while True:
        if (getUser(bet.challangee.id).hasAccepted(bet)):
            break
        await asyncio.sleep(15)
    
    

@client.slash_command(guild_ids=[guild])
async def bet(ctx, user:discord.Member, ammount:int):
    logf("user " + ctx.author.name + " challanged " + user.name + " for " + str(ammount) + " points")

    if (ammount <= 0):
        embed = discord.Embed(title="Points", description=f"You can't challange with negative chesta points", color=0x00ff00)
        await ctx.respond(embed=embed, ephemeral=True)
        return
    
    if userInList(user.id):
        if getUser(user.id).points >= ammount:
            
            logf("waiting for bet response from " + user.name)
            embed = discord.Embed(title="Bet", description="waiting for the other user to accept")
            await ctx.respond(embed=embed)
            bet = Bet(ctx.author, user, ammount)
            await awaitBetResponse(bet)
            embed = discord.Embed(title="Bet", description=f"Bet accepted, waiting for the result", color=0x00ff00)
            await ctx.respond(embed=embed, ephemeral=True)
            r = random.randint(0, 100)
            if r > 50:
                getUser(ctx.author.id).addPoints(ammount)
                getUser(user.id).removePoints(ammount)
                embed = discord.Embed(title="Points", description=f"`{ctx.author.name}` won `{ammount}` chesta points", color=0x00ff00)
                await ctx.respond(embed=embed)
            else:
                getUser(ctx.author.id).removePoints(ammount)
                getUser(user.id).addPoints(ammount)
                embed = discord.Embed(title="Points", description=f"`{user.name}` won `{ammount}` chesta points", color=0x00ff00)
                await ctx.respond(embed=embed)



        else:
            embed = discord.Embed(title="Points", description=f"They don't have enough chesta points(poor)", color=0x00ff00)
            await ctx.respond(embed=embed, ephemeral=True)

    else:
        embed = discord.Embed(title="Points", description=f"They don't have enough chesta points(poor)", color=0x00ff00)
        await ctx.respond(embed=embed, ephemeral=True)

    



@client.slash_command(guild_ids=[guild])
async def coinflip(ctx, ammount:int):
    if userInList(ctx.author.id):
        if getUser(ctx.author.id).points >= ammount:
            r = random.randint(0, 100)
            if r > 55:
                getUser(ctx.author.id).addPoints(ammount)
                embed = discord.Embed(title="Points", description=f"You won `{ammount}` chesta points", color=0x00ff00)
                await ctx.respond(embed=embed)
            else:
                getUser(ctx.author.id).removePoints(ammount)
                embed = discord.Embed(title="Points", description=f"You lost `{ammount}` chesta points", color=0x00ff00)
                await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(title="Points", description=f"You don't have enough chesta points", color=0x00ff00)
            await ctx.respond(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(title="Points", description=f"You don't have enough chesta points", color=0x00ff00)
        await ctx.respond(embed=embed, ephemeral=True)



@client.event
async def on_ready():
    logf("Bot ready")

    logf(f"""  Client Information
 > user: '{client.user}' intiialized
 > monitoring user: '{client.get_user(userId)}'
 > servers: '{client.guilds[0].name}'""")
    
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name="god motherfuckin damnnn"))

    loadUserData()
    asyncio.create_task(watchForUserUpdate())
    asyncio.create_task(scheduleTimedMessage(client.get_channel(atEveryoneChannel), (19, 24), "DAILY @everyone"))

def atExit():
    logf("saving data")
    with open("log.txt", "w") as f:
        json.dump(f, )
    if (len(users) > 0):
        saveUserData()
    
    if nextSend != 0:
        saveAteveryoneTime()


if __name__ == "__main__":
    loadLastSend()
    atexit.register(saveUserData)
    client.run(token)

