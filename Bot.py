import json
import discord
import random
import logging
import asyncio
import Set
import re

log = logging.getLogger()
VERSION = "1.1.2"


class BruhClient(discord.Client):
    async def get_key(self, guild):
        return f"{guild.id}" if (guild is not None) else None

    async def on_ready(self):
        log.info(
            "Logged in as {}, with ID {}".format(self.user.name, self.user.id)
        )
        await self.change_presence(
            activity=discord.Activity(
                name="for bruh moments", type=discord.ActivityType.watching
            )
        )

        self.servers = {}
        try:
            with open("servers.json", "r") as f:
                self.servers = json.load(f)
        except FileNotFoundError as e:
            log.exception("No server file yet")
            with open("servers.json", "w+") as f:
                json.dump(self.servers, f)

        self.intervals = {}

        for id, value in self.servers.items():
            if value["disappearing"]:
                self.intervals[id] = Set.Interval(
                    value["wipe_time"], self.wipe, id=value["wipe_channel"]
                )

    async def on_guild_join(self, guild):
        log.info("Joined guild: {}".format(guild.name))
        if guild.system_channel is not None:
            await guild.system_channel.send(
                "Hi, thanks for adding BruhBot! Use `!set` to set which channel to send to."
            )
        self.servers[self.get_key(guild)] = {
            "channel": None,
            "delete_message": False,
            "disappearing": False,
        }

    async def on_guild_remove(self, guild):
        log.info("Removed from guild: %s" % guild.name)
        self.servers.pop(await self.get_key(guild), None)
        try:
            with open("servers.json", "w") as f:
                json.dump(self.servers, f, indent=4)
        except IOError as e:
            log.error("Servers.json went missing, yikes")
            exit()

    async def on_message_delete(self, message):
        log.info("Message deletion noticed")
        if self.servers[await self.get_key(message.guild)]["delete_message"]:
            async for entry in message.guild.audit_logs(limit=10):
                if (
                    entry.action == discord.AuditLogAction.message_delete
                    and entry.target.id == message.author.id
                ):
                    log.info("Sending a delete message")
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
        log.info("Message event dispatched")
        key_name = await self.get_key(message.guild)
        if message.author.id == self.user.id:
            return
        if (
            message.author.guild_permissions.administrator
            or message.author.id == keys["admin_id"]
        ):
            if message.content.startswith("!set"):
                if key_name is not None:
                    if (
                        self.servers[key_name]["channel"] is None
                        or self.servers[key_name]["channel"]
                        != message.channel.id
                    ):
                        self.servers[key_name]["channel"] = message.channel.id
                        await message.channel.send(
                            "Set channel to %s!" % message.channel.mention
                        )
                        try:
                            log.info(
                                "Dumping channel: %s, in Guild: %s"
                                % (message.channel.name, message.guild.name)
                            )
                            with open("servers.json", "w") as f:
                                json.dump(self.servers, f, indent=4)
                        except IOError as e:
                            log.error("Servers.json went missing, yikes")
                            exit()

            elif message.content.startswith("!test"):
                log.info("Sending test message")
                await self.on_member_remove(message.author)

            elif message.content.startswith("!deltoggle"):
                self.servers[key_name]["delete_message"] = not self.servers[
                    key_name
                ]["delete_message"]
                try:
                    log.info(
                        "Dumping delete msg in Guild: %s" % (message.guild.name)
                    )
                    with open("servers.json", "w") as f:
                        json.dump(self.servers, f, indent=4)
                except IOError as e:
                    log.error("Servers.json went missing, yikes")
                    exit()
                await message.channel.send(
                    "Turned delete message on."
                    if self.servers[key_name]["delete_message"]
                    else "Turned delete message off."
                )

            elif message.content.startswith("!disappearing"):
                await message.channel.send(
                    "Turning channel wipes on."
                    if not self.servers[key_name]["disappearing"]
                    else "Turning channel wipes off."
                )

                if self.servers[key_name]["disappearing"]:
                    self.servers[key_name]["disappearing"] = False
                    self.intervals[key_name].cancel()
                else:
                    self.servers[key_name]["disappearing"] = True
                    self.servers[key_name]["wipe_channel"] = message.channel.id
                    time = re.match(r"(?:\d*\.){0,1}\d+", message.content)

                    if not time == None:
                        time = float(time)
                    else:
                        log.warning("No time provided")
                        await message.channel.send(
                            "No time provided, defaulting to 12 hours"
                        )
                        time = 0.5

                    # * hours * minutes * seconds
                    time *= 24 * 60 * 60
                    self.servers[key_name]["wipe_time"] = time

                    self.intervals[key_name] = Set.Interval(
                        time, self.wipe, message.channel.id
                    )
                try:
                    log.info("Dumping disappearing messages")
                    with open("servers.json", "w") as f:
                        json.dump(self.servers, f, indent=4)
                except IOError as e:
                    log.error("Servers.json went missing, yikes")
                    exit()

            elif message.content.startswith("!changeWipe"):
                if self.servers[key_name]["disappearing"]:
                    time = re.search(
                        "(?:\d*\.){0,1}\d+", message.content
                    ).group()

                    if not time == None:
                        time = float(time)
                        await message.channel.send(
                            "Updated the time to {} day(s)".format(time)
                        )
                    else:
                        log.warning("No time provided")
                        await message.channel.send(
                            "No time provided, defaulting to 12 hours"
                        )
                        time = 0.5

                    # * hours * minutes * seconds
                    time *= 24 * 60 * 60
                    self.servers[key_name]["wipe_time"] = time

                    self.intervals[key_name].cancel()
                    self.intervals[key_name] = Set.Interval(
                        time, self.wipe, message.channel.id
                    )
                    try:
                        log.info("Dumping disappearing messages")
                        with open("servers.json", "w") as f:
                            json.dump(self.servers, f, indent=4)
                    except IOError as e:
                        log.error("Servers.json went missing, yikes")
                        exit()

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

    def wipe(self, id):
        if id == None:
            return
        channel = self.get_channel(id)
        asyncio.run(channel.purge(limit=5000, bulk=True))
        asyncio.run(channel.send("Purged channel"))

    async def on_member_remove(self, member):
        key_name = await self.get_key(member.guild)
        if (
            key_name is not None
            and self.servers[key_name]["channel"] is not None
        ):
            channel = self.get_channel(self.servers[key_name]["channel"])
            log.info(
                "Sending message in channel: %s of Guild: %s"
                % (channel.name, member.guild.name)
            )
            await channel.send("bruh" if random.randint(0, 1) == 0 else "Bruh")


logging.basicConfig(
    format="[%(name)s][%(levelname)s] %(message)s", level=logging.INFO,
)
log.info(f"BruhBot Version: {VERSION}")

intents = discord.Intents(
    members=True,
    presences=True,
    bans=True,
    guilds=True,
    messages=True,
    reactions=True,
)
intents.members = True
intents.presences = True
client = BruhClient(intents=intents)
try:
    with open("key.json", "r") as f:
        keys = json.load(f)
        client.run(keys["token"])
except IOError as e:
    print("Key not provided, exitting")
