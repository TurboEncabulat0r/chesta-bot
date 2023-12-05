import json

class Shop():
    def __init__(self):
        self.items = []

    def addItem(self, item):
        self.items.append(item)

    def removeItem(self, item):
        self.items.remove(item)

    def getItem(self, name):
        for item in self.items:
            if (item.name == name):
                return item
        return None

    def getItems(self):
        return self.items

    def tojson(self):
        return {
            "items": [item.tojson() for item in self.items]
        }

    def save(self, path):
        with open(path, "w") as f:
            json.dump(self.tojson(), f, indent=4)

    def load(self, path):
        with open(path, "r") as f:
            data = json.load(f)
            for item in data["items"]:
                self.addItem(Item(item["name"], item["price"], item["description"], item["emoji"]))

class Item():
    def __init__(self, name, price, description, emoji):
        self.name = name
        self.price = price
        self.description = description
        self.emoji = emoji

    def tojson(self):
        return {
            "name": self.name,
            "price": self.price,
            "description": self.description,
            "emoji": self.emoji
        }