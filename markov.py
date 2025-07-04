from asyncio import sleep
import asyncio
import markovify
import re
import os
import random as r
from glob import glob


class User:
    """Contains data for individual discord users."""

    def __init__(self, name, id):
        """Initialize variable attributes."""
        self.name = name
        self.id = id
        self.text = []
        self.model = None
        self.stupid = None

    def add(self, msg_to_add):
        """Add message data to user object."""
        self.text.append(msg_to_add)

    async def create_models(self):
        """Create the markov models for the object."""
        _text = MODEL_DELIM.join(self.text)
        self.model = CustomText(_text, state_size=2)
        # Return control to the event loop to minimize the chance
        # of blocking the main thread for too long.
        await sleep(0)
        self.stupid = CustomText(_text, state_size=5)


basepath = 'dlogger/exported'

user_by_id_by_guild_id: dict[str, dict[str, User]] = dict()

emotes = []

# Columns in the CSV files
ID   = 0
USER = 1
DATE = 2
MSG  = 3
ATCH = 4
RCTN = 5

MODEL_DELIM = '}{'


class CustomText(markovify.Text):
    """Override of text model class from markovify.

    This model uses a custom delimiter that probably does
    not appear in the source text.
    """

    def sentence_split(self, text):
        """Override of a text method from markovify using the custom delimiter."""
        return re.split(fr'\s*{MODEL_DELIM}\s*', text)


def is_valid(msg):
    """Return True if the given message is valid."""
    invalidators = ['Joined the server.', 'Pinned a message.', '!get']
    prefixes = ['!', '?', '$', '[]', '.']
    return True not in ([test in msg for test in invalidators]
                      + [msg.startswith(prefix) for prefix in prefixes])


def user_from_name(name, gid):
    """Return a user object from a name fragment."""
    for user in user_by_id_by_guild_id[gid].values():
        u_name = user.name.lower()
        if u_name.startswith(name.lower()):
            return user
    return None


def user_is_blacklisted(user, gid):
    """Return True if the given User is blacklisted."""
    try:
        if not os.path.exists(os.path.join(basepath, str(gid), 'blacklist.csv')):
            return False
        with open(os.path.join(basepath, str(gid), 'blacklist.csv'), 'r') as file:
            print('checking if', user.name + ':' + user.id, 'is in blacklist:')
            return str(user.id) in file.read().split(',')
    except Exception as e:
        print('exception reading blacklist')
        print(e)
        return False


def user_blacklist(user, gid):
    """Add a user to the blacklist."""
    with open(os.path.join(basepath, str(gid), 'blacklist.csv'), 'a+') as file:
        file.write(user.id + ',')


def get_full_name(name, gid) -> str | None:
    """Return the full name of a user given a name fragment."""
    user = user_from_name(name, gid)
    if user:
        return user.name
    return None


def add_user_to_blacklist(name, gid):
    """Add a user to the blacklist if the user is not already there."""
    user = user_from_name(name, gid)
    if not user:
        pass
    elif not user_is_blacklisted(user, gid):
        user_blacklist(user, gid)
        return True
    return False


def has_emojis(sentence):
    """Return True if the given sentence contains a <:name:id> formatted emote."""
    return r'<:\s*:\s*>' in sentence


def replace_emotes(sentence):
    """Return a string with emotes replaced with a valid format.

    Emotes in input are in form :emotename: and replaced with form
    <:emotename:id_number>.
    """
    for emote in emotes:
        emote_in_text = ':' + emote.name + ':'
        emote_replace = ('<a:' if emote.animated else '<:' ) + emote.name + ':' + str(emote.id) + '>'
        sentence = sentence.replace(emote_in_text, emote_replace)
    return sentence


def emojify(sentence):
    """Replace emotes in a string with valid form for Discord."""
    try:
        return replace_emotes(sentence)
    except Exception as e:
        print('Something went wrong replacing any emotes in:', sentence)
        print(e)
        return sentence


def generate_sentence(person, num_tries, stupid):
    """Create a sentence given a User object and model signifier."""
    model = person.stupid if stupid else person.model
    print('state size =', model.state_size)
    sentence = model.make_sentence(tries=num_tries)
    if sentence is None:
        raise RuntimeError('Sentence is None')
    else:
        return sentence


def return_one(gid, name='', num_tries=500,  stupid=False):
    """Return a nicely-formatted sentence for a given username."""
    try:
        print('\nTrying to return one sentence from', name)
        person = user_from_name(name, gid)
        sentence = generate_sentence(person, num_tries, stupid)
        return process_sentence(person, sentence)
    except Exception as e:
        print('failed to create sentence for ' + name)
        print(e)
        return None


def process_sentence(person, sentence):
    """Return a list with properly formatted name and sentence items."""
    return ['**' + person.name + '**:  ', emojify(sentence)]


def return_one_with_emote(gid):
    """Try to return a sentence that includes a formatted emote."""
    while True:
        person = r.choice(list(user_by_id_by_guild_id[gid].values()))
        message = return_one(person.name, num_tries=250)
        if message and has_emojis(message[1]):
            return message


def get_people(gid):
    """Return a list with all stored User object names."""
    return [x.name for x in user_by_id_by_guild_id[gid].values()]


def id_in_user_list(id, gid):
    """Return True if user id exists."""
    return id in user_by_id_by_guild_id[gid]


def add_user(name, id, gid):
    """Add a new user object to the list."""
    user_by_id_by_guild_id[gid][id] = User(name, id)


def get_user(id, gid):
    """Return a User object given an id."""
    return user_by_id_by_guild_id[gid].get(id, None)


async def import_users_from_list(data, gid):
    """Given a list of Discord message data, create User objects with relevant information."""
    for line in data:
        # print('+'+line)
        _user = None
        try:
            _entry = line.split('","')
            if '**Discord HTTPException**' in line or len(_entry) < 4:
                continue # hack to keep NotSoBot from breaking this code
            _id = _entry[ID].strip('"')
            _user = _entry[USER]
            _name, _ = _user.split('#', maxsplit=1)
            _msg = _entry[MSG]
            # _reactions = _entry[RCTN].strip('"') # throws OOB

            get_or_create_user(gid, _id, _name).add(_msg)
        except Exception as e:
            print(e)
            print('line:', line)
            print('user:', _user)


def get_or_create_user(gid, id: str, name: str):
    return user_by_id_by_guild_id[gid].setdefault(id, User(name, id))


async def create_user_models(gid):
    """Create text models for each existing user."""
    for user in user_by_id_by_guild_id[gid].values():
        try:
            await user.create_models()
        except Exception as e:
            print('failed to create model for', user.name)


def invalid_file(filename, gid):
    path = os.path.join(basepath, str(gid), 'blockedchannels.txt')

    if not os.path.exists(path):
        return False
    with open(path) as f:
        for _id in f:
            if _id.strip() in filename:
                print('ignoring channel with id', _id.strip())
                return True
    return False


async def import_chat_logs(gid):
    """Read the message CSVs."""
    messages = []
    for filename in glob(os.path.join(basepath, str(gid), '*.csv')):
        if invalid_file(filename, gid):
            continue
        with open(filename, 'r', encoding='utf-8') as file:
            messages.extend(file.read().split('\n')[1:-1])
    return messages


async def import_therealus(gid):
    messages = []
    for filename in glob(os.path.join(basepath, str(gid), '*the-real-us*.csv')):
        with open(filename, 'r', encoding='utf-8') as file:
            entries = file.read().split('\n')[1:-1]
            messages.extend([e for e in entries if '"497602687211143189",' in e])
    return messages


async def import_usbot_user(gid):
    for line in await import_therealus(gid):
        #print('+'+line)
        _entry = line.split('","')
        if '**Discord HTTPException**' in line or len(_entry) < 4:
            continue # hack to keep NotSoBot from breaking this code
        _id = _entry[ID].strip('"')
        _user = _entry[USER]
        _name, _ = _user.split('#', maxsplit=1)
        _msg = _entry[MSG]
        # _reactions = _entry[RCTN].strip('"') # throws OOB

        get_or_create_user(gid, _id, _name).add(_msg)



async def init(gids):
    print(gids)
    guild_process_tasks = [process_guild_logs(gid) for gid in gids]
    await asyncio.gather(*guild_process_tasks)
    print('done with init')


async def process_guild_logs(gid):
    print('updating gid', gid)
    messages = await import_chat_logs(gid)
    user_by_id_by_guild_id[gid] = dict()
    await import_users_from_list(messages, gid)
    await import_usbot_user(gid)
    await create_user_models(gid)
    print('done with markov for', gid, 'with', len(user_by_id_by_guild_id[gid]), 'users')
    