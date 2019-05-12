# discord-markov
This program utilizes markovify to make new sentences based on discord users.


# Information
Currently undergoing a rewrite. It also requires a lot of bodging to set up and make work with any given server. 

`emojilist.py` contains custom emotes that the bot might use. It must be manually updated with possible emotes. In the future, the bot will automagically gather emote information from guilds it is a member of.

## Installation
Requires discord.py and markovify.

```
pip install discord
pip install markovify
```

I used DiscordCharExporter.CLI to get and store chats to csv files. Change the variable `filepath` in `discord_markov.py` to the filepath that contains your chat logs.
