# -*- coding: utf-8 -*-

import markovify
import re
import random as r
from emojilist import emotelist
import traceback as tb


filepath = '.\\chats\\exported\\'
filenames = ['do.csv','dont.csv','nofbipls.csv','therealus.csv','bodgeneral.csv']

users = []
user_list = []

USER = 0
DATE = 1
MSG  = 2
ATCH = 3

class User:
    def __init__(self,name,id):
        self.name = name
        self.id = id
        self.text = []
        self.model = None

    def add(self,msg_to_add):
        self.text.append(msg_to_add)

    def create_normal_model(self):
        _text = '}{'.join(self.text)
        self.model = CustomText(_text, state_size=2)

    def return_stupid_model(self):
        text = '}{'.join(self.text)
        return CustomText(text, state_size=5)

class CustomText(markovify.Text):
    def sentence_split(self, text):
        return re.split(r'\s*}{\s*', text)

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
    model = person.return_stupid_model() if stupid else person.model
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

def __init__():
    global users
    global user_list

    users = []
    user_list = []
    messages = []

    for name in filenames:
        with open(filepath + name, 'r', encoding='utf-8') as file:
            messages.extend(file.read().split('\n')[1:-1])
    with open('blacklist.csv', 'r') as blacklist_in:
        blacklist = blacklist_in.read().split(',')
    for line in messages:
        entry = line.split(';')
        user = entry[USER]
        msg = entry[MSG]
        name = user.split('#')[0]
        id = user.split('#')[1]
        if id not in users:
            users.append(id)
            user_list.append(User(name,id))
        for x in range(len(user_list)):
            if user_list[x].id == id and id not in blacklist:
                #print('id')
                if is_valid(msg):
                    user_list[x].add(msg)
    for user in user_list:
        try:
            user.create_normal_model()
        except Exception as e:
            print('failed to create model for', user.name)

__init__()
