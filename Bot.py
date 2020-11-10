import json, discord, random, re

VERSION = "0.3.3"
print("BruhBot Version: %s" % VERSION)


class BruhClient(discord.Client):
    async def get_key(self, guild):
        return "%s" % guild.id if (guild is not None) else None

    async def on_ready(self):
        print("Logged in as %s, with ID %s" % (self.user.name, self.user.id))
        await self.change_presence(
            activity=discord.Activity(
                name="for bruh moments", type=discord.ActivityType.watching
            )
        )
        self.cache = None

    async def on_guild_join(self, guild):
        print("Joined guild: %s" % guild.name)
        if guild.system_channel is not None:
            await guild.system_channel.send(
                "Hi, thanks for adding BruhBot! Use `!set` to set which channel to send to."
            )
        d[self.get_key(guild)] = {"channel": None, "delete_message": False}

    async def on_guild_remove(self, guild):
        print("Removed from guild: %s" % guild.name)
        d.pop(await self.get_key(guild), None)
        try:
            with open("key.json", "w") as f:
                json.dump(d, f, indent=4)
        except IOError as e:
            print("Key.json went missing, yikes")
            exit()

    async def on_message_delete(self, message):
        print("Message deletion noticed")
        if d[await self.get_key(message.guild)]["delete_message"]:
            async for entry in message.guild.audit_logs(limit=10):
                if (
                    entry.action == discord.AuditLogAction.message_delete
                    and entry.target.id == message.author.id
                ):
                    print("Sending a delete message")
                    user_string = (
                        message.author.mention
                        if message.author.mention is not None
                        else message.author.name + message.author.discriminator
                    )
                    await message.channel.send(
                        "%s had a bruh moment" % user_string
                    )
                    break

    async def on_message(self, message):
        print("Message event dispatched")
        key_name = await self.get_key(message.guild)
        if message.author.id == self.user.id:
            return
        if (
            message.author.guild_permissions.administrator
            or message.author.id == d["admin_id"]
        ):
            if message.content.startswith("!set"):
                if key_name is not None:
                    if (
                        d[key_name]["channel"] is None
                        or d[key_name]["channel"] != message.channel.id
                    ):
                        d[key_name]["channel"] = message.channel.id
                        await message.channel.send(
                            "Set channel to %s!" % message.channel.mention
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
            elif message.content.startswith("!test"):
                print("Sending test message")
                await self.on_member_remove(message.author)
            elif message.content.startswith("!deltoggle"):
                d[key_name]["delete_message"] = not d[key_name][
                    "delete_message"
                ]
                try:
                    print(
                        "Dumping delete msg in Guild: %s" % (message.guild.name)
                    )
                    with open("key.json", "w") as f:
                        json.dump(d, f, indent=4)
                except IOError as e:
                    print("Key.json went missing, yikes")
                    exit()
                await message.channel.send(
                    "Turned delete message on."
                    if d[key_name]["delete_message"]
                    else "Turned delete message off."
                )
        if message.content.startswith("!bruh"):
            await message.channel.send("%s bruh" % message.author.mention)
        elif message.content.startswith("!bhelp"):
            await message.channel.send(
                """Hi I'm BruhBot!
My commands are:
```!bhelp: sends this message.
!bruh: sends bruh back.
!set*: sets the channel to send leave messages to.
!deltoggle*: toggles message delete messages.
!test*: sends a test message.```
* admin only commands"""
            )
        else:
            return

    async def on_member_remove(self, member):
        key_name = await self.get_key(member.guild)
        if key_name is not None and d[key_name]["channel"] is not None:
            channel = self.get_channel(d[key_name]["channel"])
            print(
                "Sending message in channel: %s of Guild: %s"
                % (channel.name, member.guild.name)
            )
            await channel.send("bruh" if random.randint(0, 1) == 0 else "Bruh")


intents = discord.Intents.default()
intents.members = True
client = BruhClient(intents=intents)
try:
    with open("key.json", "r") as f:
        d = json.load(f)
        client.run(d["token"])
except IOError as e:
    print("Key not provided, exitting")
