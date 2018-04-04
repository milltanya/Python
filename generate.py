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
                    default='',
                    type=str,
                    help="path to the file where the text will locate",
                    dest='out')
par = parser.parse_args()

f = open(par.mod[0], 'r')
data = {}
for line in f:
    tmp = line.split()
    tmp1 = data.pop(tmp[0], {})
    tmp1.update({tmp[1]: int(tmp[2])})
    data.update({tmp[0]: tmp1})
f.close()

length = par.len[0]
if par.seed == "":
    k = random.randint(0, len(data)-1)
    i = 0
    for j in data:
        i += 1
        if i == k:
            break
    word = j
else:
    word = par.seed[0]
k = 0
if word == 'END':
    word = 'BEGIN'
if word == "BEGIN":
    s = ''
else:
    s = word


def weighted_choice(choices):
    total = sum(choices[c] for c in choices)
    r = random.uniform(0, total)
    upto = 0
    for c in choices:
        if upto + choices[c] >= r:
            return c
        upto += choices[c]
    assert False, "Shouldn't get here"


while (k < length):
    next_word = weighted_choice(data.get(word, {}))
    if next_word != 'END':
        s = s + " " + next_word
        word = next_word
        k += 1
    else:
        word = "BEGIN"

if par.out == "":
    print(s)
else:
    f = open(par.out[0], 'w')
    f.write(s)
    f.close()
