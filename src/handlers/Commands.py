import discord, logging
from typing import Dict

log = logging.getLogger(__name__)

# region Admin commands
async def set(parent, message: discord.Message, entry: Dict[str, str]) -> bool:
    """Sets the greeting channel

    Args:
        parent (BruhClient): The parent bot instance
        message (discord.Message): The message asking for the setting
        entry (Dict[str, str]): The entry for the guild change

    Returns:
        bool: Success status
    """
    if not "channel" in entry or entry["channel"] != message.channel.id:
        entry["channel"] = message.channel.id
        log.info(
            f"Updated to channel: {message.channel.name}, in Guild: {message.guild.name}"
        )
        await parent.dump_json()

        await message.channel.send(
            embed=discord.Embed(
                title="Set channel",
                description="I'll say bruh in this channel from now on",
                color=discord.Color.green(),
            )
        )
        return True

    elif entry["channel"] == message.channel.id:
        log.info(f"No op channel update to Guild: {message.guild.name}")
        await message.channel.send(
            embed=discord.Embed(
                title="Set channel",
                description="I already say bruh here! Did you mean a different channel?",
                color=discord.Color.gold(),
            )
        )
        return True

    else:
        await message.channel.send(
            embed=discord.Embed(
                title="Set channel",
                description="I have no idea how you ended up here! Error",
                color=discord.Color.red(),
            )
        )
        log.warn(
            f"Set channel messed up somehow. Guild: {message.guild.name}, entry: {entry}"
        )
        return False


async def test(parent, message: discord.Message) -> None:
    """Sends a test message

    Args:
        parent (BruhClient): The parent bot instance
        message (discord.Message): The message asking for a test
    """
    log.info(f"Sending a test message in {message.guild.name}")
    await parent.on_member_remove(
        message.author, addOn=f"(latency: {parent.latency}s)"
    )
    return


async def delToggle(
    parent, message: discord.Message, entry: Dict[str, str]
) -> None:
    """Toggles the message deletion behavior

    Args:
        parent (BruhClient): The parent bot instance
        message (discord.Message): The message asking to toggle the behavior
        entry (Dict[str, str]): The guild entry for the guild being changed
    """
    entry["delete_message"] = not entry["delete_message"]
    log.info(f"Dumping delete msg in Guild: {message.guild.name}")
    parent.dump_json()

    desc = (
        "I'll say something if I think someone had a bruh moment"
        if entry["delete_message"]
        else "I'll keep quiet :)"
    )
    await message.channel.send(
        embed=discord.Embed(
            title="Deletion message toggled",
            description=desc,
            color=discord.Color.green(),
        )
    )
    return


async def changePrefix(
    parent, message: discord.Message, entry: dict[str, str], prefix: str
):
    """Changes the command prefix

    Args:
        parent (BruhClient): The parent bot instance
        message (discord.Message): The message asking to change
        entry (dict[str,str]): The entry for the server asking
    """
    split = message.content.split()
    new_prefix = split[-1]

    if len(split) > 1 and (
        not "prefix" in entry or entry["prefix"] != new_prefix
    ):
        log.info(f"Guild: {message.guild.name} changed prefix")
        entry["prefix"] = new_prefix
        await parent.dump_json()
        await message.channel.send(
            embed=discord.Embed(
                title="Command prefix updated",
                description=f'The command prefix has changed from "{prefix}" to "{new_prefix}"!',
                color=discord.Color.green(),
            )
        )
    elif entry["prefix"] == new_prefix:
        await message.channel.send(
            embed=discord.Embed(
                title="Command prefix unchanged",
                description=f'The command prefix was already "{new_prefix}"! Try again if you want to change it!',
                color=discord.Color.gold(),
            )
        )
    elif len(split) == 1:
        await message.channel.send(
            embed=discord.Embed(
                title="Command prefix unchanged",
                description=f"You didn't provide a new prefix, try again.",
                color=discord.Color.red(),
            )
        )

    return


# endregion
async def bruh(message: discord.Message) -> None:
    """Sends bruh back to a user

    Args:
        message (discord.Message): The message asking to be bruh'd
    """
    await message.channel.send(f"{message.author.mention} bruh")
    return


async def help(message: discord.Message, prefix: str) -> None:
    """Sends the help message

    Args:
        message (discord.Message): The message asking for help
    """
    embed = discord.Embed(
        title="BruhBot Help",
        description="Hi, I'm BruhBot! (he/him)",
        color=discord.Color.green(),
    )
    embed.add_field(
        name=f"{prefix}bruhHelp", value="Shows this help message", inline=False
    )
    embed.add_field(
        name=f"{prefix}bruh", value="I'll say bruh back to you", inline=False
    )
    embed.add_field(
        name=f"{prefix}set",
        value="Admin only - Sets where I'll say bruh when people leave",
        inline=False,
    )
    embed.add_field(
        name=f"{prefix}test",
        value="Admin only - Simulates someone leaving, and gives my latency",
        inline=False,
    )
    embed.add_field(
        name=f"{prefix}delToggle",
        value="Admin only - Toggles whether I say something when I think someone had a message deleted by a mod",
        inline=False,
    )
    embed.add_field(
        name=f"{prefix}changePrefix <new prefix>",
        value="Admin only - Changes my command prefix. I'll pick the last part of the message that has a space in front of it.",
        inline=False,
    )

    await message.channel.send(embed=embed)
    return
