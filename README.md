# discord-markov
This program utilizes the package `markovify` to make new sentences based on discord users.

Currently undergoing a rewrite. It also requires a lot of bodging to set up and make work with any given server. 

`emojilist.py` contains custom emotes that the bot might use. It must be manually updated with possible emotes. In the future, the bot will automagically gather emote information from guilds it is a member of.

## Installation
Requires discord.py and markovify.

```
pip install discord
pip install markovify
```

I used DiscordCharExporter.CLI to get and store chats to csv files. Change the variable `filepath` in `discord_markov.py` to the filepath that contains your chat logs.

Store your bot's secret key in a text file named `secret.txt` in the base folder.

## Commands
All commands are prefixed with `!`

* `get` - Generates 2-5 sentences from users that are not blacklisted and sends them to the text channel in which the command was sent.
* `get <user>` - Generates one sentence for the specified user and sends it to the text channel in which the command was sent.
* `getstupid <user>` - Experimental command that generates and sends a message for the specified user with a text model state size of 5 instead of the default 2.
* `say <string>` - Copies the text `<string>` and sends it back after passing it through the emote replacer method.
* `tts` - Toggles if the bot sends messages with text-to-speech on or off.
* `list` - DMs the user a list of all valid usernames to use with the various `get` commands
* `blacklist <user>` - Adds a user to the blacklist of users to pull from. A blacklisted user will never appear in the `get` command. Useful for users that end up with the same message sent every time the command is called.
