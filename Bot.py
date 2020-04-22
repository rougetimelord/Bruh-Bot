import json, discord


class BruhClient(discord.Client):
    async def on_ready(self):
        print("Logged in as %s, with ID %s" % (self.name, self.user_id))

    async def on_message(self, message):
        if message.author.id == self.user_id:
            return
        elif (
            message.content.startswith("!set")
            and message.author.server_permissions.administrator
        ):
            d["channel-id"] = message.channel.id
            await message.channel.send(
                "Set channel to %s!" % message.channel.name
            )
        else:
            return

    async def on_member_remove(self, member):
        guild = member.guild
        if True:
            pass


client = discord.BruhClient()
try:
    with open(key.json, "r") as f:
        d = json.load(f)
        client.run(d["token"])
except IOError as e:
    print("Key not provided, exitting")
    exit()
