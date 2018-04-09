import random
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


def download_model(input_file, data):
    f = open(input_file, 'r')
    for line in f:
        words = line.split()
        first_word_data = data.pop(words[0], {})
        first_word_data.update({words[1]: int(words[2])})
        data.update({words[0]: first_word_data})
    f.close()


def weighted_choice(choices):
    total = sum(choices[c] for c in choices)
    r = random.uniform(0, total)
    upto = 0
    for c in choices:
        if upto + choices[c] >= r:
            return c
        upto += choices[c]
    return random.sample(data.keys(), 1)[0]


def print_word(word, output_file):
    if output_file == "stdout":
        print(word, end='')
    else:
        f.write(word)


data = {}
download_model(par.mod[0], data)
if par.seed == "":
    cur_word = random.sample(data.keys(), 1)[0]
else:
    cur_word = par.seed[0]
if par.out[0] != "stdout":
    f = open(par.out[0], 'w')
print_word(cur_word, par.out[0])
for i in range(par.len[0] - 1):
    next_word = weighted_choice(data.get(cur_word, {}))
    print_word(" " + next_word, par.out[0])
    cur_word = next_word
if par.out[0] != "stdout":
    f.close()
