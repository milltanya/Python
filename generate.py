import random
import sys
import numpy
import pymorphy2
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--model ',
                    action='store',
                    nargs=1,
                    type=str,
                    required=True,
                    help="path to the file where the model locates",
                    dest='mod')
parser.add_argument('--seed',
                    action='store',
                    nargs=1,
                    default='',
                    type=str,
                    help="first word",
                    dest='seed')
parser.add_argument('--length',
                    action='store',
                    nargs=1,
                    type=int,
                    required=True,
                    help="length",
                    dest='len')
parser.add_argument('--output ',
                    action='store',
                    nargs=1,
                    default=['stdout'],
                    type=str,
                    help="path to the file where the text will locate",
                    dest='out')
par = parser.parse_args()


def add_pair(first_word, second_word, freq, data):
    first_word_data = data.pop(first_word, {})
    first_word_data.update({second_word: freq})
    data.update({first_word: first_word_data})


def download_model(input_file):
    f = open(input_file, 'r')
    data = [False, {}, {}]
    for line in f:
        if line == "lex\n":
            pass
        elif line == "morph\n":
            data[0] = True
        else:
            words = line.split()
            if not data[0]:
                add_pair(words[0], ' '.join(words[1:-1]), int(words[-1]), data[1])
            else:
                add_pair(words[0], ' '.join(words[1:-1]), int(words[-1]), data[2])
    f.close()
    return data


def print_word(word):
    if "text" not in dir(print_word):
        print_word.text = ""
    if word == "\n":
        print(print_word.text)
        print_word.text = ""
    else:
        if print_word.text != "":
            print_word.text += " "
        print_word.text += word
        if len(print_word.text) > 100:
            print(print_word.text)
            print_word.text = ""


def choice(data):
    if data == {}:
        return ""
    else:
        new_words = [elem for elem in data]
        total = sum(data.values())
        probs = [elem / total for elem in data.values()]
        return numpy.random.choice(new_words, 1, probs)[0]


def generate(data, seed, length):
    cur_word = seed
    print_word(cur_word)
    for i in range(length - 1):
        next_word = choice(data[1].get(cur_word, {}))
        if next_word == "":
            next_word = random.sample(data[1].keys(), 1)[0]
        print_word(next_word)
        cur_word = next_word
    print_word("\n")


def morph_generate(data, seed, length):
    morph = pymorphy2.MorphAnalyzer()
    cur_word = seed
    print_word(cur_word)
    for i in range(length - 1):
        next_lex = choice(data[1].get(cur_word, {}))
        if next_lex == "":
            next_word = random.sample(data[1].keys(), 1)[0]
        else:
            next_lexemes = []
            for elem in morph.parse(next_lex):
                next_lexemes = next_lexemes + elem.lexeme
            morph_data = data[2].get(cur_word, {})
            flag = False
            while (not flag) and morph_data != {}:
                next_morph = choice(morph_data)
                next_morphemes = next_morph.split()
                for lexeme in next_lexemes:
                    flag = True
                    for morpheme in next_morphemes:
                        if morpheme not in lexeme.tag:
                            flag = False
                            break
                    if flag:
                        next_word = lexeme.word
                        break
                morph_data.pop(next_morph, {})
            if not flag:
                next_word = next_lex
        print_word(next_word)
        cur_word = next_word
    print_word("\n")


data = download_model(par.mod[0])
if par.seed == "":
    seed = random.sample(data[1].keys(), 1)[0]
else:
    seed = par.seed[0]
if par.out[0] != "stdout":
    sys.stdout = open(par.out[0], 'w')
if data[0]:
    morph_generate(data, seed, par.len[0])
else:
    generate(data, seed, par.len[0])
if par.out[0] != "stdout":
    sys.stdout.close()
