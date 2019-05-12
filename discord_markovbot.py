import discord
import discord_markov
import random as r
import traceback as tb
import sys
import time

client = discord.Client()

do_tts = False

# TODO:
# add timestamps to logs

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
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
    channel_to_send = message.channel
    if ' ' in message.content:  # get name
        await command_get_specified(message, name=name_from_command(message))
    else:                       # get a few random
        await command_get_unspecified(message)

async def command_get_specified(message, name, stupid=False):
    msg = ''
    async with message.channel.typing():
        if not name:
            msg = 'Error: specified user does not exist'
        else:
            msg = generate_message(name, num_tries=500, stupid=stupid)
    await message.channel.send(msg, tts=do_tts)

async def command_get_unspecified(message):
    for x in range(int(r.random() * 3 + 2)):
        while True:
            with message.channel.typing():
                name = get_random_name()
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
    await command_get_specified(message, name=name_from_command(message), stupid=True)

async def command_debug_emote(message):
    progress_text = await message.channel.send('This might take a while.')
    with message.channel.typing():
        msg_data = discord_markov.return_one_with_emote()
        print(msg_data)
        msg = format_message(msg_data)
    await progress_text.delete()
    await message.channel.send(msg, tts=do_tts)

async def command_say(message):
    try:
        print(message.content)
        msg = message.content[message.content.index(' ') + 1:]
        msg = discord_markov.emojify(msg)
        print(msg)
        await message.channel.send(msg)
    except BaseException as e:
        print("error on testmessage")
        print(type(e), str(e))
        tb.print_exc()

async def command_toggle(message):
    global do_tts
    do_tts = not do_tts
    await message.delete()
    await message.channel.send('TTS ' + ('Enabled' if do_tts else 'Disabled'), delete_after=5)

async def command_list(message):
    list = '\n'.join(discord_markov.get_people())
    msg = '```' + list + '```'
    await message.author.send(msg)

async def command_partyrockers(message):
    await message.channel.send('se tonight')

async def command_blacklist(message):
    if not message.author.id == 173978157349601283:
        await send_error(message, err_type='perms')
    username = name_from_command(message)
    success = discord_markov.blacklist_user(username)
    msg_out = ''
    if success:
        msg_out = username + ' will no longer send messages here.'
    else:
        msg_out = username + ' could not be blacklisted or is already blacklisted.'
    await message.channel.send(msg_out)

async def send_error(message, err_type='generic'):
    error = 'Error: '
    if err_type == 'generic':
        error += '¯\\_(ツ)_/¯'
    elif err_type == 'perms':
        error += 'you do not have permission to do that'
    await message.channel.send(error)

def format_message(msg_data):
    return '.\n' + msg_data[0] + msg_data[1]

def name_from_command(message):
    return discord_markov.get_full_name(' '.join(message.content.split(' ')[1:]))

def generate_message(name, num_tries=250, stupid=False):
    msg = discord_markov.return_one(name=name, num_tries=num_tries, stupid=stupid)
    if msg is not None:
        print('succeeded')
        print(msg)
        msg = format_message(msg)
    else:
        msg = 'Error: cannot create message from ' + name
    return msg

def get_random_name():
    while True:
        name = r.choice(discord_markov.get_people())
        if not discord_markov.user_blacklisted(discord_markov.user_from_name(name)):
            return name

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

file = open('secret.txt')
secret = file.read()
file.close()
client.run(secret)
