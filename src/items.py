import builtins
import discord 
import asyncio
import random


items = []

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

class Item():
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.attributes = []
        self.id = 0
        self.description = ""
        self.image = ""
        self.onUse = None
        self.onDaily = None



