# UsBot

UsBot is a Discord bot that utilizes the package `markovify` to make new sentences based on Discord users. Click [here](https://discord.com/api/oauth2/authorize?client_id=837517727488933889&permissions=343104&scope=bot) to add it to your sever! The bot will step you through the setup process.

Report any issues you experience to the Issues tab on this GitHub repo.

> ### Note:
>
> The message fetching portion of the bot is not open source. This means that if you want to use this code to make your own bot, you will have to write that yourself. I do not recommend doing this.

## Commands

All commands are prefixed with `us.`

- `get` - Generates 2-5 sentences from users that are not blacklisted and sends them to the text channel in which the command was sent.
- `get <user>` - Generates one sentence for the specified user and sends it to the text channel in which the command was sent. UsBot will do its best to autocomplete a partial name!
- `getstupid <user>` - Experimental command that generates and sends a message for the specified user with a text model state size of 5 instead of the default 2.
- `say <string>` - Copies the text `<string>` and sends it back after passing it through the emote replacer method.
- `tts` - Toggles if the bot sends messages with text-to-speech on or off.
- `list` - DMs the user a list of all valid usernames to use with the various `get` commands
- `blacklist <user>` - Adds a user to the blacklist of users to pull from. A blacklisted user will never appear in the `get` command. Useful for users that end up with the same message sent every time the command is called.
- `blockchannel <#text-channel>` - Blocks a channel from being incorporated into user generation models. This should be used on any channel used for bot commands or other types of spam.
- `unblockchannel <#text-channel>` - Unblocks a channel that was previously blocked.

## Developing

1. Activate the virtual environment with `./.venv/Scripts/activate`
