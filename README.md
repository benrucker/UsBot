# discord-markov
This program utilizes markovify to make new sentences based on discord users.


# Information
Currently undergoing a rewrite. It also requires a lot of bodging to set up and make work with any given server. 


## Installation
Requires discord.py and markovify.

```
pip install discord
pip install markovify
```

I used DiscordCharExporter.CLI to get and store chats to csv files. Change the variable `filepath` in `discord_markov.py` to the filepath that contains your chat logs.
