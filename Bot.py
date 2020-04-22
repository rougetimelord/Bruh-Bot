import json, discord, random


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
            guild = message.guild
            if guild != None:
                g_id = guild.id
                key_name = "%s_channel" % g_id
                d[key_name] = message.channel.id
                await message.channel.send(
                    "Set channel to %s!" % message.channel.name
                )
                try:
                    with open("key.json", "w") as f:
                        json.dump(d, f, indent=4)
                except IOError as e:
                    print("Key.json went missing, yikes")
                    exit(self, 1)
        else:
            return

    async def on_member_remove(self, member):
        guild = member.guild
        key_name = "%s_channel" % guild.id
        if key_name in d:
            channel = self.get_channel(d[key_name])
            msg = "bruh" if random.randint(0, 1) == 0 else "Bruh"
            await channel.send(msg)


client = BruhClient()
try:
    with open("key.json", "r") as f:
        d = json.load(f)
        client.run(d["token"])
except IOError as e:
    print("Key not provided, exitting")
    exit()
