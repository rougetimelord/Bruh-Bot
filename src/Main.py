import logging, json, discord
from .BruhClient import BruhClient
from .VERSION import VERSION as VERSION

log = logging.getLogger()


def main():
    logging.basicConfig(
        format="{%(asctime)s} [%(name)s][%(levelname)s] %(message)s",
        level=logging.INFO,
        handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    )
    log.info(f"BruhBot Version: {VERSION}")

    try:
        with open("data/key.json", "r") as f:
            keys = json.load(f)
            intents = discord.Intents(
                members=True,
                presences=True,
                bans=True,
                guilds=True,
                messages=True,
                reactions=True,
            )
            client: BruhClient = BruhClient(intents=intents, keys=keys)
            client.run(keys["token"])
    except (IOError, FileNotFoundError):
        print("Key not provided, exiting")
        return
