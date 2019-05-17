import markovify
import re
import os
import random as r
import traceback as tb
from glob import glob
from emojilist import emotelist

filepath = 'E:\\Documents\\Discord\\chat logs\\exported\\'

users = []
user_list = []

USER = 0
DATE = 1
MSG  = 2
ATCH = 3

MODEL_DELIM = '}{'


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

    def create_models(self):
        """Create the markov models for the object."""
        _text = MODEL_DELIM.join(self.text)
        self.model = CustomText(_text, state_size=2)
        self.stupid = CustomText(_text, state_size=5)


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
    invalidators = ['Joined the server.', 'Pinned a message.', ':  ', '!get']
    return True not in [test in msg for test in invalidators]


def user_from_name(name):
    """Return a user object from a name fragment."""
    for user in user_list:
        u_name = user.name.lower()
        if u_name.startswith(name.lower()):
            return user
    return None


def user_is_blacklisted(user):
    """Return True if the given User is blacklisted."""
    try:
        with open('blacklist.csv', 'r') as file:
            return user.id in file.read().split(',')
    except Exception as e:
        return False


def user_blacklist(user):
    """Add a user to the blacklist."""
    with open('blacklist.csv', 'a+') as file:
        file.write(user.id + ',')


def get_full_name(name):
    """Return the full name of a user given a name fragment."""
    user = user_from_name(name)
    if user:
        return user.name
    return None


def add_user_to_blacklist(name):
    """Add a user to the blacklist if the user is not already there."""
    user = user_from_name(name)
    if not user:
        pass
    elif not user_is_blacklisted(user):
        user_blacklist(user)
        return True
    return False


def has_emojis(sentence):
    """Return True if the given sentence contains a <:name:id> formatted emote."""
    return r'<:\s*:\s*>'


def replace_emotes(sentence):
    """Return a string with emotes replaced with a valid format.

    Emotes in input are in form :emotename: and replaced with form
    <:emotename:id_number>.
    """
    for emote in emotelist.keys():
        sentence = sentence.replace(emote, emotelist[emote])
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


def return_one(name='', num_tries=500,  stupid=False):
    """Return a nicely-formatted sentence for a given username."""
    try:
        print('\n\nTrying to return one sentence from', name)
        person = user_from_name(name)
        sentence = generate_sentence(person, num_tries, stupid)
        return process_sentence(person, sentence)
    except Exception as e:
        print('failed to create sentence for ' + person.name)
        print(e)
        return None


def process_sentence(person, sentence):
    """Return a list with properly formatted name and sentence items."""
    return ['**' + person.name + '**:  ', emojify(sentence)]


def return_one_with_emote():
    """Try to return a sentence that includes a formatted emote."""
    while True:
        person = r.choice(user_list)
        message = return_one(person, 250)
        if message and has_emojis(message[1]):
            return message


def get_people():
    """Return a list with all stored User object names."""
    return [x.name for x in user_list]


def id_in_user_list(id):
    """Return True if user id exists."""
    for user in user_list:
        if user.id == id:
            return True
    return False


def add_user(name, id):
    """Add a new user object to the list."""
    global user_list
    user_list.append(User(name, id))


def get_user(id):
    """Return a User object given an id."""
    for user in user_list:
        if user.id == id:
            return user
    return None


def import_users_from_list(data):
    """Given a list of Discord message data, create User objects with relevant information."""
    for line in data:
        _entry = line.split(';')
        _user = _entry[USER]
        _msg = _entry[MSG]
        _name, _id = _user.split('#')
        if not id_in_user_list(_id):
            add_user(_name, _id)
        if is_valid(_msg):
            get_user(_id).add(_msg)


def create_user_models():
    """Create text models for each existing user."""
    global user_list
    for user in user_list:
        try:
            user.create_models()
        except Exception as e:
            # print(e)
            print('failed to create model for', user.name)


def import_chat_logs():
    """Transform external message data into a list."""
    messages = []
    for filename in glob(os.path.join(filepath, '*.csv')):
        with open(filename, 'r', encoding='utf-8') as file:
            messages.extend(file.read().split('\n')[1:-1])
    return messages


def __init__():
    global users
    global user_list
    users = []
    user_list = []
    messages = import_chat_logs()
    import_users_from_list(messages)
    create_user_models()


__init__()
