# -*- coding: utf-8 -*-

import markovify
import re
import os
import glob
import random as r
import traceback as tb
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
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.text = []
        self.model = None
        self.stupid = None

    def add(self, msg_to_add):
        self.text.append(msg_to_add)

    def create_models(self):
        _text = MODEL_DELIM.join(self.text)
        self.model = CustomText(_text, state_size=2)
        self.stupid = CustomText(_text, state_size=5)

class CustomText(markovify.Text):
    def sentence_split(self, text):
        return re.split(fr'\s*{MODEL_DELIM}\s*', text)

def is_valid(msg):
    invalidators = ['Joined the server.','Pinned a message.',':  ','!get']
    for str in invalidators:
        if str in msg:
            return False
    return True

def user_from_name(name):
    for user in user_list:
        u_name = user.name.lower()
        if u_name.startswith(name.lower()):
            return user
    return None

def user_blacklisted(user):
    with open('blacklist.csv', 'r') as file:
        return user.id in file.read().split(',')

def user_blacklist(user):
    with open('blacklist.csv', 'a') as file:
        file.write(',' + user.id)

def get_full_name(name):
    user = user_from_name(name)
    if user:
        return user.name
    return None

def blacklist_user(name):
    user = user_from_name(name)
    if not user:
        pass
    elif not user_blacklisted(user):
        user_blacklist(user)
        return True
    return False

def replace_emotes(sentence):
    for emote in emotelist.keys():
        sentence = sentence.replace(emote, emotelist[emote])
    return sentence

def emojify(sentence):
    try:
        return replace_emotes(sentence)
    except:
        print('Something went wrong replacing any emotes in:',sentence)
        return sentence

def generate_sentence(person, num_tries, stupid):
    model = person.stupid if stupid else person.model
    print('state size =', model.state_size)
    sentence = model.make_sentence(tries=num_tries)
    if sentence is None:
        raise RuntimeError('Sentence is None')
    else:
        return sentence

def return_one(name='', num_tries=500,  stupid=False):
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
    return format_message(person, emojify(sentence))

def format_message(person, sentence):
    return ['**' + person.name + '**:  ',str(sentence)]

def return_one_with_emote():
    while True:
        person = r.choice(user_list)
        message = return_one(person, 250)
        if message and has_emojis(message[1]):
            break
    return message

def get_people():
    return [x.name for x in user_list]

def id_in_user_list(id):
    for user in user_list:
        if user.id == id:
            return True
    return False

def add_user(name, id):
    global user_list
    user_list.append(User(name, id))

def get_user(id):
    for user in user_list:
        if user.id == id:
            return user
    return None

def import_users_from_list(data):
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
    global user_list
    for user in user_list:
        try:
            user.create_models()
        except Exception as e:
            print('failed to create model for', user.name)

def import_chat_logs():
    messages = []
    for filename in glob.glob(os.path.join(filepath, '*.csv')):
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
