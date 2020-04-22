import json, discord

client = discord.Client()


@client.event
async def on_ready():
    print("Logged in as %s" % client.user)


try:
    with open(key.json, "r") as f:
        d = json.load(f)
        client.run(d["token"])
except IOError as e:
    print("Key not provided, exitting")
    exit()
