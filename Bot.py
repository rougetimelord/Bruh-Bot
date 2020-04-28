import json, discord, random

VERSION = "0.1.5"
print("BruhBot Version: %s" % VERSION)


class BruhClient(discord.Client):
    async def get_key(self, guild):
        return "%s_channel" % guild.id if (guild is not None) else None

    async def on_ready(self):
        print("Logged in as %s, with ID %s" % (self.user.name, self.user.id))
        await self.change_presence(
            activity=discord.Activity(
                name="for bruh moments", type=discord.ActivityType.watching
            )
        )

    async def on_guild_join(self, guild):
        print("Joined guild: %s" % guild.name)
        if guild.system_channel is not None:
            await guild.system_channel.send(
                "Hi, thanks for adding BruhBot! Use `!set` to set which channel to send to."
            )

    async def on_guild_remove(self, guild):
        print("Removed from guild: %s" % guild.name)
        d.pop(await self.get_key(guild), None)
        try:
            with open("key.json", "w") as f:
                json.dump(d, f, indent=4)
        except IOError as e:
            print("Key.json went missing, yikes")
            exit()

    async def on_message(self, message):
        print("Message event dispatched")
        key_name = await self.get_key(message.guild)
        if message.author.id == self.user.id:
            return
        if (
            message.content.startswith("!set")
            and message.author.guild_permissions.administrator
        ):
            if key_name is not None:
                if not key_name in d or d[key_name] != message.channel.id:
                    d[key_name] = message.channel.id
                    await message.channel.send(
                        "Set channel to `%s`!" % message.channel.mention
                    )
                    try:
                        print(
                            "Dumping channel: %s, in Guild: %s"
                            % (message.channel.name, message.guild.name)
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
            print("Sending test message")
            await self.on_member_remove(message.author)
        else:
            return

    async def on_member_remove(self, member):
        key_name = await self.get_key(member.guild)
        if key_name is not None and key_name in d:
            channel = self.get_channel(d[key_name])
            print(
                "Sending message in channel: %s of Guild: %s"
                % (channel.name, member.guild.name)
            )
            await channel.send("bruh" if random.randint(0, 1) == 0 else "Bruh")


client = BruhClient()
try:
    with open("key.json", "r") as f:
        d = json.load(f)
        client.run(d["token"])
except IOError as e:
    print("Key not provided, exitting")
