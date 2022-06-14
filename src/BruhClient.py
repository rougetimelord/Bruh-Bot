import discord, random, json, logging
from . import handlers
from .VERSION import VERSION as VERSION
from cachetools import TTLCache
from typing import Dict

log = logging.getLogger(__name__)


class BruhClient(discord.Client):
    def __init__(self, **kwargs) -> None:
        self.keys = kwargs["keys"]
        super().__init__(**kwargs)

    # region Helpers
    async def get_guild_entry(self, input) -> str:
        if isinstance(input, discord.Guild):
            return (
                self.servers[str(input.id)]
                if str(input.id) in self.servers
                else None
            )
        elif isinstance(input, discord.Message) or isinstance(
            input, discord.Member
        ):
            return (
                self.servers[str(input.guild.id)]
                if str(input.guild.id) in self.servers
                else None
            )
        else:
            return None

    @staticmethod
    async def check_admin(member: discord.Member) -> bool:
        """Checks if a member is an admin in the guild

        Args:
            member (discord.Member): The member to check

        Returns:
            bool: If the member is an admin
        """
        return member.guild_permissions.administrator

    async def check_owner(self, member: discord.Member) -> bool:
        """Checks if a member is the bot's owner

        Args:
            member (discord.Member): The member to check

        Returns:
            bool: If the supplied member is bot owner
        """
        info = await self.application_info()
        return info.owner.id == member.id

    async def dump_json(self) -> None:
        """Dump server data to file"""
        try:
            with open("data/servers.json", "w") as f:
                json.dump(self.servers, f, indent=4)
        except (IOError, FileNotFoundError):
            log.error("Servers.json went missing, yikes")
            with open("data/servers.json", "w+") as f:
                json.dump(self.servers, f, indent=4)

    # endregion

    # region Events
    async def on_ready(self) -> None:
        self.prefix: str = "!"
        log.info(f"Logged in as {self.user.name}, with ID {self.user.id}")
        await self.change_presence(
            activity=discord.Activity(
                name=f"for bruh moments | version: v{VERSION} | help: {self.prefix}bruhHelp",
                type=discord.ActivityType.watching,
            )
        )
        self.minuteCache = TTLCache(maxsize=100, ttl=60)
        self.servers: Dict[str, str] = {}
        try:
            with open("data/servers.json", "r") as f:
                self.servers = json.load(f)
        except FileNotFoundError as e:
            log.exception("No server file yet")
            self.dump_json()

    async def on_guild_join(self, guild: discord.Guild):
        await handlers.Membership.join(self, guild)

    async def on_guild_remove(self, guild: discord.Guild):
        await handlers.Membership.remove(self, guild)

    async def on_message_delete(self, message: discord.Message):
        log.info("Message deletion noticed")
        if self.servers[await BruhClient.get_key(message)]["delete_message"]:
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
        if message.author.bot:
            return

        guild_entry: Dict[str, str] = await self.get_guild_entry(message)
        if guild_entry == None:
            log.warning(f"Failed to get guild entry for {message.guild.name}")
            return

        prefix = (
            self.prefix
            if not "prefix" in guild_entry
            else guild_entry["prefix"]
        )

        if await BruhClient.check_admin(
            message.author
        ) or await self.check_owner(message.author):
            if message.content.startswith(f"{prefix}set"):
                await handlers.Commands.set(self, message, guild_entry)
            elif message.content.startswith(f"{prefix}test"):
                await handlers.Commands.test(self, message)
            elif message.content.startswith(f"{prefix}delToggle"):
                await handlers.Commands.delToggle(self, message, guild_entry)
            elif message.content.startswith(
                f"{prefix}changePrefix"
            ) or message.content.startswith(f"{self.prefix}changePrefix"):
                await handlers.Commands.changePrefix(
                    self, message, guild_entry, prefix
                )

        if (
            message.content.startswith(f"{prefix}help")
            or message.content.startswith(f"{prefix}bruhhelp")
            or message.content.startswith(f"{self.prefix}help")
            or message.content.startswith(f"{self.prefix}bruhHelp")
        ):
            await handlers.Commands.help(message, prefix)
        elif message.content.startswith("!bruh"):
            await handlers.Commands.bruh(message)

        return

    async def on_member_join(self, member: discord.Member):
        self.minuteCache[member.id] = 1

    async def on_member_remove(self, member: discord.Member, addOn=""):
        key_name = await BruhClient.get_key(member)
        if (
            key_name is not None
            and self.servers[key_name]["channel"] is not None
        ):
            channel: discord.TextChannel = self.get_channel(
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

    # endregion
