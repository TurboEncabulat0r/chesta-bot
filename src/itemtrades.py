import discord, asyncio
from discord.ext import commands
import random, json, os, builtins
from helpers import * 
import users
import atexit
guild = builtins.guild
client = builtins.client

"""
users are able to trade requst other ursers, sending them a dm. they can use the trade command to accept or deny the trade

commands:
    trade - request a trade with a user
    trade accept - accept a trade request
    trade deny - deny a trade request
    trade cancel - cancel a trade request
    trade add - add an item to a trade
    trade remove - remove an item from a trade
    trade list - list the items in a trade
    trade send - send a trade request
    trade clear - clear a trade request
    trade complete - complete a trade


"""

class Trade():
    def __init__(self, user):
        self.user = user
        self.items = []
        self.otherUser = None
        self.otherItems = []
        self.accepted = False
        self.sent = False
        self.completed = False
        self.message = None
        self.id = random.randint(0, 100000)