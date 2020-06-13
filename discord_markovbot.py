import discord
import discord_markov
import random as r
import traceback as tb
import sys
import time

client = discord.Client()
do_tts = False


@client.event
async def on_message(message):
    """Call the necessary method upon user command."""
    if message.author == client.user:
        return

    if message.content.startswith('!tts'):
        await command_toggle(message)
    elif message.content.startswith('!getstupid'):
        await command_get_stupid(message)
    elif message.content.startswith('!get'):
        await command_get(message)
    elif message.content.startswith('!debug emote'):
        await command_debug_emote(message)
    elif message.content.startswith('!say'):
        await command_say(message)
    elif message.content.startswith('!partyrockersinthehou'):
        await command_partyrockers(message)
    elif message.content.startswith('!list'):
        await command_list(message)
    elif message.content.startswith('!blacklist'):
        await command_blacklist(message)
    elif message.content.startswith('!die'):
        sys.exit(0)


async def command_get(message):
    """Send a message based on one or a few users."""
    if ' ' in message.content:  # get name
        await command_get_specified(message, name=name_from_command(message))
    else:                       # get a few random
        await command_get_unspecified(message)


async def command_get_specified(message, name, num_tries=500, stupid=False):
    """Send a message based on a specific user."""
    msg = ''
    async with message.channel.typing():
        if not name:
            msg = 'Error: specified user does not exist'
        else:
            msg = generate_message(name, num_tries=num_tries, stupid=stupid)
    await message.channel.send(msg, tts=do_tts)


async def command_get_unspecified(message):
    """Send multiple messages based on randomly chosen users.

    Will not send a message based on a user more than once in one invocation.
    """
    names = []
    for x in range(int(r.random() * 3 + 2)):
        while True:
            with message.channel.typing():
                name = get_random_name()
                if name in names:
                    continue
                names.append(name)
                msg = generate_message(name, num_tries=250)
                if msg.startswith('Error'):
                    print("failed, continuing")
                    continue
                else:
                    print("succeeded")
                    print(msg)
            await message.channel.send(msg, tts=do_tts)
            break


async def command_get_stupid(message):
    """Send a message based on a specific user with a different text model."""
    _name = name_from_command(message)
    await command_get_specified(message, name=_name, num_tries=100000, stupid=True)


async def command_debug_emote(message):
    """Send a message that contains an emote."""
    progress_text = await message.channel.send('This might take a while.')
    async with message.channel.typing():
        msg_data = discord_markov.return_one_with_emote()
        print(msg_data)
        msg = format_message(msg_data)
    await progress_text.delete()
    await message.channel.send(msg, tts=do_tts)


async def command_say(message):
    """Send a message containing just the user's input parameters."""
    try:
        print(message.content)
        msg = ' '.join(message.content.split(' ')[1:])
        msg = discord_markov.emojify(msg)
        print(msg)
        await message.channel.send(msg)
    except BaseException as e:
        print("error on testmessage")
        print(type(e), str(e))
        tb.print_exc()


async def command_toggle(message):
    """Toggle tts on or off."""
    global do_tts
    do_tts = not do_tts
    await message.delete()
    await message.channel.send('TTS ' + ('Enabled' if do_tts else 'Disabled'), delete_after=5)


async def command_list(message):
    """Send to the user a list of all valid usernames."""
    list = '\n'.join(discord_markov.get_people())
    msg = '```' + list + '```'
    await message.author.send(msg)


async def command_partyrockers(message):
    """Meme."""
    await message.channel.send('se tonight')


async def command_blacklist(message):
    """Blacklist a user."""
    if not message.author.id == 173978157349601283:
        await send_error(message, err_type='perms')

    username = name_from_command(message)
    success = discord_markov.add_user_to_blacklist(username)
    msg_out = ''
    if success:
        msg_out = username + ' will no longer send messages here.'
    else:
        msg_out = username + ' could not be blacklisted or is already blacklisted.'
    await message.channel.send(msg_out)


async def send_error(message, err_type='generic'):
    """User-facing error handler."""
    error = 'Error: '
    if err_type == 'generic':
        error += '¯\\_(ツ)_/¯'
    elif err_type == 'perms':
        error += 'you do not have permission to do that'
    await message.channel.send(error)


def format_message(msg_data):
    """Format message data; return string."""
    return ''.join(msg_data)


def name_from_command(message):
    """Return a valid username given a username fragment in a command."""
    return discord_markov.get_full_name(' '.join(message.content.split(' ')[1:]))


def generate_message(name, num_tries=250, stupid=False):
    """Return a new sentence based on user name."""
    msg = discord_markov.return_one(name=name, num_tries=num_tries, stupid=stupid)
    if msg is not None:
        print('succeeded')
        print(msg)
        msg = format_message(msg)
    else:
        msg = 'Error: cannot create message from ' + name
    return msg


def get_random_name():
    """Return a random full username that isn't blacklisted."""
    while True:
        name = r.choice(discord_markov.get_people())
        if not discord_markov.user_is_blacklisted(discord_markov.user_from_name(name)):
            return name


@client.event
async def on_ready():
    """Print when ready."""
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    discord_markov.init_emotes(client.emojis)


file = open('secret.txt')
secret = file.read()
file.close()
client.run(secret)
