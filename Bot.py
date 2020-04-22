import json, discord, random


class BruhClient(discord.Client):
    async def on_ready(self):
        print("Logged in as %s, with ID %s" % (self.user.name, self.user.id))

    async def on_guild_join(self, guild):
        print("Joined guild: %s" % guild.name)
        if guild.system_channel is not None:
            await guild.system_channel.send(
                "Hi! Thanks for adding BruhBot, to set the channel that I should send to send `!set` in that channel. Send `!test` to send a test message."
            )

    async def on_guild_remove(self, guild):
        print("Removed from guild: %s" % guild.name)
        key_name = "%s_channel" % guild.id
        d.pop(key_name, None)
        try:
            print("Dumping leaving Guild: %s" % guild.name)
            with open("key.json", "w") as f:
                json.dump(d, f, indent=4)
        except IOError as e:
            print("Key.json went missing, yikes")
            exit()

    async def on_message(self, message):
        print("Message event dispatched")
        if message.author.id == self.user.id:
            return
        elif (
            message.content.startswith("!set")
            and message.author.guild_permissions.administrator
        ):
            guild = message.guild
            if guild != None:
                key_name = "%s_channel" % guild.id
                if not key_name in d or d[key_name] != message.channel.id:
                    d[key_name] = message.channel.id
                    await message.channel.send(
                        "Set channel to `%s`!" % message.channel.name
                    )
                    try:
                        print(
                            "Dumping channel: %s, in Guild: %s"
                            % (message.channel.name, guild.name)
                        )
                        with open("key.json", "w") as f:
                            json.dump(d, f, indent=4)
                    except IOError as e:
                        print("Key.json went missing, yikes")
                        exit()
        elif (
            message.content.startswith("!test")
            and message.author.guild_permissions.administrator
        ):
            await self.on_member_remove(message.author)
        else:
            return

    async def on_member_remove(self, member):
        guild = member.guild
        key_name = "%s_channel" % guild.id
        if key_name in d:
            channel = self.get_channel(d[key_name])
            msg = "bruh" if random.randint(0, 1) == 0 else "Bruh"
            print(
                "Sending message in channel: %s of Guild: %s"
                % (channel.name, guild.name)
            )
            await channel.send(msg)


client = BruhClient()
try:
    with open("key.json", "r") as f:
        d = json.load(f)
        client.run(d["token"])
except IOError as e:
    print("Key not provided, exitting")
    exit()
