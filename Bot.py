import json, discord
from discord.ext import commands


class BruhClient(discord.Client):
    async def on_ready(self):
        print("Logged in as %s" % client.user)


d = ""
client = discord.BruhClient()
try:
    with open(key.json, "r") as f:
        d = json.load(f)
        client.run(d["token"])
except IOError as e:
    print("Key not provided, exitting")
    exit()
