import discord
import random, Set, re, json
import logging, asyncio
from cachetools import TTLCache
from typing import Dict

log = logging.getLogger()
VERSION = "1.2.5"


class BruhClient(discord.Client):
    def __init__(self, **kwargs) -> None:
        self.keys = kwargs["keys"]
        super().__init__(**kwargs)

    async def get_key(self, guild: discord.Guild) -> str:
        return f"{guild.id}" if (guild is not None) else None

    async def on_ready(self):
        log.info(f"Logged in as {self.user.name}, with ID {self.user.id}")
        await self.change_presence(
            activity=discord.Activity(
                name="for bruh moments", type=discord.ActivityType.watching
            )
        )

        self.minuteCache = TTLCache(maxsize=100, ttl=60)
        self.servers: Dict[str, str] = {}
        try:
            with open("servers.json", "r") as f:
                self.servers = json.load(f)
        except FileNotFoundError as e:
            log.exception("No server file yet")
            with open("servers.json", "w+") as f:
                json.dump(self.servers, f)

        self.intervals: Dict[str, Set.Interval] = {}

        for id, value in self.servers.items():
            if value["disappearing"]:
                self.intervals[id] = Set.Interval(
                    value["wipe_time"], self.wipe, id=value["wipe_channel"]
                )

    async def on_guild_join(self, guild: discord.Guild):
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

    async def on_guild_remove(self, guild: discord.Guild):
        log.info("Removed from guild: %s" % guild.name)
        self.servers.pop(await self.get_key(guild), None)
        try:
            with open("servers.json", "w") as f:
                json.dump(self.servers, f, indent=4)
        except IOError as e:
            log.error("Servers.json went missing, yikes")
            exit()

    async def on_message_delete(self, message: discord.Message):
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
                        f"{user_string} had a bruh moment"
                    )
                    break

    async def on_message(self, message: discord.Message):
        log.info("Message event dispatched")
        key_name = await self.get_key(message.guild)
        if message.author.id == self.user.id:
            return
        if (
            message.author.guild_permissions.administrator
            or message.author.id == self.keys["admin_id"]
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
                            f"Set channel to {message.channel.mention}!"
                        )
                        try:
                            log.info(
                                f"Dumping channel: {message.channel.name}, in Guild: {message.guild.name}"
                            )
                            with open("servers.json", "w") as f:
                                json.dump(self.servers, f, indent=4)
                        except IOError as e:
                            log.error("Servers.json went missing, yikes")
                            exit()

            elif message.content.startswith("!test"):
                log.info("Sending test message")
                add = f"(latency: {self.latency}s)"
                await self.on_member_remove(message.author, add)

            elif message.content.startswith("!deltoggle"):
                self.servers[key_name]["delete_message"] = not self.servers[
                    key_name
                ]["delete_message"]
                try:
                    log.info(
                        f"Dumping delete msg in Guild: {message.guild.name}"
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
                            f"Updated the time to {time} day(s)"
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
            await message.channel.send(f"{message.author.mention} bruh")
        elif message.content.startswith("!bhelp"):
            await message.channel.send(
                """Hi I'm BruhBot!
My commands are:
```!bhelp: sends this message.
!bruh: sends bruh back.
!set*: sets the channel to send leave messages to.
!deltoggle*: toggles message delete messages.
!test*: sends a test message.
!disappearing* {time in days}: sets the channel that the message is sent in as a wipe channel, which wipes every x days
!changeWipe* {time in days}: changes how often the channel is wiped```
* admin only commands"""
            )
        else:
            return

    def wipe(self, id):
        if id == None:
            return
        channel: discord.abc.GuildChannel = self.get_channel(id)
        asyncio.run(channel.purge(limit=5000, bulk=True))
        asyncio.run(channel.send("Purged channel"))

    async def on_member_join(self, member: discord.Member):
        self.minuteCache[member.id] = 1

    async def on_member_remove(self, member: discord.Member, addOn=""):
        key_name = await self.get_key(member.guild)
        if (
            key_name is not None
            and self.servers[key_name]["channel"] is not None
        ):
            channel: discord.abc.GuildChannel = self.get_channel(
                self.servers[key_name]["channel"]
            )
            log.info(
                f"Sending message in channel: {channel.name} of Guild: {member.guild.name}"
            )
            if member.id in self.minuteCache.keys():
                await channel.send("BRUH")
                return
            await channel.send(
                f"bruh {addOn}"
                if random.randint(0, 1) == 0
                else f"Bruh {addOn}"
            )


def main():
    logging.basicConfig(
        format="{%(asctime)s} [%(name)s][%(levelname)s] %(message)s",
        level=logging.INFO,
        handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    )
    log.info(f"BruhBot Version: {VERSION}")

    try:
        with open("key.json", "r") as f:
            keys = json.load(f)
            intents = discord.Intents(
                members=True,
                presences=True,
                bans=True,
                guilds=True,
                messages=True,
                reactions=True,
            )
            client: discord.Client = BruhClient(intents=intents, keys=keys)
            client.run(keys["token"])
    except IOError as e:
        print("Key not provided, exiting")


if __name__ == "__main__":
    main()
