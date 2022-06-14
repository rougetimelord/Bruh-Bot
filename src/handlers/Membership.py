import discord, logging

log = logging.getLogger(__name__)


async def join(parent, guild: discord.Guild):
    log.info("Joined guild: {}".format(guild.name))
    if guild.system_channel is not None:
        await guild.system_channel.send(
            "Hi, thanks for adding BruhBot! Use `!set` to set which channel to send to."
        )
    parent.servers[BruhClient.get_key(guild)] = {
        "channel": None,
        "delete_message": False,
    }
    parent.dump_json()


async def remove(parent, guild: discord.Guild):
    log.info("Removed from guild: %s" % guild.name)
    parent.servers.pop(await BruhClient.get_key(guild), None)
    parent.dump_json()
