import discord, asyncio
from discord.ext import commands
import random, json, os, builtins
from helpers import * 
import users
guild = builtins.guild
client = builtins.client

"""
the goal here is to track users time in vc and give them points for it

stores total time in vc in arbetrary data on users
commands:
    vc - get your vc time
    vc top - get the top 10 vc times
    vc reset - reset your vc time
    vc reset all - reset everyones vc time
    vc leaderboard - get the top 10 vc times
"""

@client.slash_command(guild_ids=[guild], description="get your vc time")
async def vc(ctx, user: discord.Member = None):
    if user == None:
        user = ctx.author
    u = users.getUser(user)
    t = 0
    try:
        t = u.getArbitraryData("vcTime")
    except:
        u.addArbitraryData("vcTime", 0)
    embed = discord.Embed(title="VC Time", description=f"Your vc time is `{formatTime(t)}`", color=0x00ff00)
    await ctx.respond(embed=embed, ephemeral=True)

@client.slash_command(guild_ids=[guild], description="get the top 10 vc times")
async def vc_top(ctx):
    top = []
    for u in users.users:
        try:
            top.append({
                "name": u.name,
                "time": u.getArbitraryData("vcTime")
            })
        except:
            pass
    top.sort(key=lambda x: x['time'], reverse=True)
    top = top[:10]
    embed = discord.Embed(title="Top 10 vc times", description="The top 10 vc times are:", color=0x00ff00)
    for i in range(len(top)):
        embed.add_field(name=f"{i + 1}. {top[i]['name']}", value=f"`{formatTime(top[i]['time'])}`", inline=True)
    await ctx.respond(embed=embed, ephemeral=True)

vcData = []
async def calculateAwards(user, time):
    minuites = time / 60
    points = round(minuites / 2)
    user.addPoints(points)
    logf(f"awarded {points} points to {user.name} for {formatTime(time)} in vc")
    if (points > 30):
        await dmUser(user, f"You have been awarded {points} points for spending {formatTime(time)} in vc")

async def handleMemberJoin(member, vc):
    # check if they are in vcData
    found = False
    for d in vcData:
        if d['id'] == member.id:
            found = True
            break
    if not found:
        logf(f"detected user {member.name} joining vc")
        vcData.append({
            "id": member.id,
            "startTime": time.time()
        })

async def handleMemberLeave(member, vc):
    # get the data for the member
    data = None
    for d in vcData:
        if d['id'] == member:
            data = d
            break
    if data:
        # calculate the time they were in vc
        timeInVC = time.time() - data['startTime']
        user = users.getUser(member)
        logf(f"detected user {user.name} leaving vc after {formatTime(timeInVC)}")
        # add the time to their total time
        
        d = 0
        try:
            d = user.getArbitraryData("vcTime")
        except:
            user.addArbitraryData("vcTime", 0) 
        user.setArbitrayData("vcTime", round(d + timeInVC, 2))
        await calculateAwards(user, timeInVC)
        # remove them from vcData
        vcData.remove(data)

savedMembers = []
async def vcScanner():
    while True:
        vcs = []  
        # gets all the voice channels in the server
        g = client.get_guild(guild)
        for channel in g.voice_channels:
            vcs.append(channel)

        # loop through all the voice channels
        for vc in vcs:
            # loop through all the members in the voice channel
            for member in vc.members:
                # if they are not in savedMembers, add them and call handleMemberJoin
                if member.id not in savedMembers:
                    data = {"id": member.id, "vcid": vc.id}
                    savedMembers.append(data)
                    await handleMemberJoin(member, vc)
                # if they are in savedMembers, do nothing
                else:
                    pass
            # loop through all the members in savedMembers, if it is thier origin vcid and they are not in the vc, call handleMemberLeave
            for member in savedMembers:
                if member['vcid'] == vc.id:
                    if member['id'] not in [m.id for m in vc.members]:
                        await handleMemberLeave(member['id'], vc)
                        savedMembers.remove(member)

        await asyncio.sleep(15)