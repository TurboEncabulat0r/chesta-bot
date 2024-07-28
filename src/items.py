import builtins
import discord 
import asyncio
import random
import users
import time

chestaItemPath = "items/chesta.json"
userItemPath = "items/user.json"

items = []



attributes = {}

def AttribFunc(name):
    def inner(func):
        attributes[name] = func
        return func
    return inner

def CallAttribute(name, user):
    if name in attributes:
        attributes[name](user)

@AttribFunc("GeneratePts")
def GeneratePts(user):
    pass

@AttribFunc("IncMessagePTS")
def IncMessagePTS(user):
    pass

@AttribFunc("IncMessageChance")
def IncMessageChance(user):
    pass

@AttribFunc("IncDailyBonus")
def IncDailyBonus(user):
    pass

@AttribFunc("IncVcRewards")
def IncVcRewards(user):
    pass

@AttribFunc("IncDailyTime")
def IncDailyTime(user):
    pass

@AttribFunc("RandQuoteandPts")
def RandQuoteandPts(user):
    pass




# grants the daily points to all users
async def GrantDailyPoints():
    for user in users.users:
        user.addPoints(user.dailyBonus)
        await user.send(f"god mf damn you got `{user.dailyBonus}` daily cp :mindblown: ")


lastDaily = 0
async def Daily():
    global lastDaily
    while True:
        # wait till the next calander day to grant points
        # needs to be during the hours of 10am to 9pm
        currentTime = time.time()
        lastDaily = currentTime
        await asyncio.sleep(86400)
        


async def Hourly():
    while True:
        # call hourly for all users

        # wait 1 hour
        await asyncio.sleep(3600)


class Attribute():
    def __init__(self, name, value):
        self.name = name
        self.description = ""
        self.id = 0
        self.onUse = None
        self.onDaily = None
        self.onHour = None
        self.onEquip = None

    def use(self, user):
        pass

    def daily(self, user):
        pass

    def hourly(self, user):
        pass

    def equip(self, user):
        pass

    def unequip(self, user):
        pass

class InventoryItem():
    def __init__(self, item, amount):
        self.item = item
        self.amount = amount

    def use(self, user):
        self.item.use(user)


class Item():
    def __init__(self, name, price):
        self.name = name
        self.price = price
        self.id = 0

        # owner user, if none chesta is owner
        self.owner = None

        self.attributes = []

        self.description = ""
        self.image = ""


        self.onUse = None
        self.onDaily = None

    def use(self, user):
        pass

    def daily(self, user):
        pass

    def equip(self, user):
        pass

    def unequip(self, user):
        pass

    def loadFromJson(self, data):
        self.name = data["name"]
        self.price = data["price"]
        self.id = data["id"]
        self.description = data["description"]
        self.image = data["image"]
        self.onUse = data["onUse"]
        self.onDaily = data["onDaily"]
        self.attributes = data["attributes"]

    def saveToJson(self):
        return {
            "name": self.name,
            "price": self.price,
            "id": self.id,
            "description": self.description,
            "image": self.image,
            "onUse": self.onUse,
            "onDaily": self.onDaily,
            "attributes": self.attributes
        }
    




