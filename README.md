# Bruh Bot
A simple discord bot that says bruh every time someone leaves the server. Runs on Discord.py. [There is a node port of this bot](https://github.com/rougetimelord/BruhBotNode).

## Using the Hosted Bot
* The invite link is [this](https://discord.com/api/oauth2/authorize?client_id=702644157692379267&permissions=70323392&scope=bot).
* The bot will message your guild's system channel with a setup message. If there is no system channel, use `!set` in a channel that is accessible to the bot.
* Bot uptime is not guaranteed, it will be up when I can have it up. It may go down at any time for any reason.

## Self Hosting
To self host the bot:
* Run `pip install -r requirements.txt`.
* Replace `token` in `key_example.json`, and rename the file to `key.json`. 

## Disclaimers
* The developer (me) is not liable for the accuracy, usefulness or availability of this bot.
* This bot will only store the ID of your server and the ID of the channel to send to. (Don't believe me? Audit the code)
  * Message content is not stored or read beyond checking for commands
  * No user IDs are stored longer than one minute (new members IDs are stored in a TTL cache for an easter egg) 
* This software is provided as is with no warranty. (I literally coded this in 3 hours as a joke)
