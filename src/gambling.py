import discord
from discord.ext import commands
import asyncio
import builtins
import users
import random 
import PIL
from PIL import Image
from helpers import *

guild = builtins.guild
client = builtins.client

rouletteImagePath = "img/roul.png"
rouletteImage = PIL.Image.open(rouletteImagePath)
# commands
# roulette - start a roulette game
# roulette bet - bet on a space, takes in a string for a place on the roulette wheel and an int for the amount to bet

class Roulette():
    def __init__(self, user):
        self.bets = []
        self.id = user
        self.specialSpaces = ["0", "red", "black", "even", "odd", "1st12", "2nd12", "3rd12"]
        self.spaces = [str(i) for i in range(1, 37)]

    def addBet(self, space, bet):
        self.bets.append({
            "space": space,
            "bet": bet
        })
    
    def isSpace(self, space):
        return space in self.specialSpaces or space in self.spaces
    
    def getSpaceInfo(self, space):
        #uses the space string to get the color and if it is even or odd

        twelve = (int(space) // 12) + 1

        if space == "00" or space == "0":
            return {
                "color": "green",
                "even": False,
                "twelve": None
            }
        elif int(space) % 2 == 0:
            return {
                "color": "red",
                "even": True,
                "twelve": twelve
            }
        
        else:
            return {
                "color": "black",
                "even": False,
                "twelve": twelve
            }

    def getRandomSpace(self):
        newSpaces = self.spaces
        newSpaces.append("0")
        return random.choice(self.spaces)

    def spin(self):
        return self.getRandomSpace()
    
    def refund(self):
        for bet in self.bets:
            users.getUser(self.id).addPoints(bet["bet"])

        self.bets = []

    def payout(self, space):
        info = self.getSpaceInfo(space)
        money = 0
        embed = discord.Embed(title=f"**{space} ({info['color']})**", color=0x00ff00)

        for bet in self.bets:
            m = 0
            if bet["space"] == space:
                m = bet["bet"] * 36
            elif bet["space"] == info["color"]:
                if info["color"] == "green":
                    m = bet["bet"] * 18
                else:
                    m = bet["bet"] * 2
            elif bet["space"] == "even" and info["even"]:
                m = bet["bet"] * 2
            elif bet["space"] == "odd" and not info["even"]:
                m = bet["bet"] * 2
            elif bet["space"] == "1st12" and info["twelve"] == 1:
                m = bet["bet"] * 3
            elif bet["space"] == "2nd12" and info["twelve"] == 2:
                m = bet["bet"] * 3
            elif bet["space"] == "3rd12" and info["twelve"] == 3:
                m = bet["bet"] * 3

            money += m

        # adds fields for all the spaces and points the user betted on, they should all be on multiple lines
        for i,bet in enumerate(self.bets):
            embed.add_field(name=f"Bet {i} - `{bet['space']}`", value=f"`${bet['bet']} cp`", inline=False)

        embed.add_field(name="Winnings", value=f"`${money} cp`")
        users.getUser(self.id).addPoints(money)
        

        return embed


    def clearBets(self):
        self.bets = []


# what does cp stand for
# chesta points
        
games = []
@client.slash_command(guild=client.get_guild(guild))
async def roulette(ctx):
    id = ctx.author.id
    for game in games:
        if game[0] == id:
            await roulette_spin(ctx)
            return
        
    r = Roulette(id)
    games.append([id, r])
    embed = discord.Embed(title="Roulette", description=f"You started a roulette game", color=0x00ff00)
    embed.add_field(name="How to play", value="Use `/roulette_bet` to bet on a space on the roulette wheel, then use `/roulette` again to spin")
    embed.add_field(name="Spaces/Rewards", value="`0 - 36` (x36), N-st12 (x3), `red`, `black`, `even`, `odd` (x2)")
    
    # attach image
    img = discord.File(rouletteImagePath, filename="roulette.png")
    embed.set_image(url="attachment://roulette.png")
    await ctx.respond(embed=embed, ephemeral=True, file=img)

#@client.slash_command(guild_ids=[guild])
async def roulette_spin(ctx):

    user = users.getUser(ctx.author.id)
    if (user == None):
        embed = discord.Embed(title="Points", description=f"You don't have enough chesta points", color=0x00ff00)
        await ctx.respond(embed=embed, ephemeral=True)
        return
    
    for game in games:
        if game[0] == ctx.author.id:
            space = game[1].spin()
            embed = game[1].payout(space)
            await ctx.respond(embed=embed)
            games.remove(game)
            return
    else:
        embed = discord.Embed(title="Roulette", description=f"You don't have a roulette game", color=0x00ff00)
        await ctx.respond(embed=embed, ephemeral=True)

@client.slash_command(guild=client.get_guild(guild))
async def roulette_refund(ctx):
    for game in games:
        if game[0] == ctx.author.id:
            game[1].refund()
            embed = discord.Embed(title="Roulette", description=f"You were refunded", color=0x00ff00)
            await ctx.respond(embed=embed)
            return
    else:
        embed = discord.Embed(title="Roulette", description=f"You don't have a roulette game", color=0x00ff00)
        await ctx.respond(embed=embed, ephemeral=True)

@client.slash_command(guild=client.get_guild(guild))
async def roulette_bet(ctx, space:str , bet: int):
    user = users.getUser(ctx.author.id)
    if (user == None):
        embed = discord.Embed(title="Roulette", description=f"You don't have enough chesta points", color=0x00ff00)
        await ctx.respond(embed=embed, ephemeral=True)
        return
    if (user.points < bet):
        embed = discord.Embed(title="Roulette", description=f"You don't have enough chesta points", color=0x00ff00)
        await ctx.respond(embed=embed, ephemeral=True)
        return
    
    if (bet < 0):
        embed = discord.Embed(title="Roulette", description=f"You can't bet negative chesta points", color=0x00ff00)
        await ctx.respond(embed=embed, ephemeral=True)
        return
    
    for game in games:
        if game[0] == ctx.author.id:
            if not game[1].isSpace(space):
                embed = discord.Embed(title="Roulette", description=f"`{space}` is not a valid space", color=0x00ff00)
                await ctx.respond(embed=embed, ephemeral=True)
                return
            
            game[1].addBet(space, bet)
            user.removePoints(bet)
            embed = discord.Embed(title="Roulette", description=f"You bet `{bet}` chesta points on `{space}`", color=0x00ff00)
            await ctx.respond(embed=embed, ephemeral=True)
            return
    else:
        embed = discord.Embed(title="Roulette", description=f"You don't have a roulette game", color=0x00ff00)
        await ctx.respond(embed=embed, ephemeral=True)

@client.slash_command(guild_ids=[guild])
async def slots(ctx, bet: int):
    await ctx.respond("This command is not yet implemented.", ephemeral=True)


@client.slash_command(guild=client.get_guild(guild))
async def coinflip(ctx, ammount:int):
    if users.userInList(ctx.author.id):
        if users.getUser(ctx.author.id).points >= ammount:
            r = random.randint(0, 100)
            if r > 55:
                users.getUser(ctx.author.id).addPoints(ammount)
                embed = discord.Embed(title="Points", description=f"You won `{ammount}` chesta points", color=0x00ff00)
                await ctx.respond(embed=embed)
            else:
                users.getUser(ctx.author.id).removePoints(ammount)
                embed = discord.Embed(title="Points", description=f"You lost `{ammount}` chesta points", color=0x00ff00)
                await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(title="Points", description=f"You don't have enough chesta points", color=0x00ff00)
            await ctx.respond(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(title="Points", description=f"You don't have enough chesta points", color=0x00ff00)
        await ctx.respond(embed=embed, ephemeral=True)