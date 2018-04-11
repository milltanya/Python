import re
import argparse
import pymorphy2
import os

parser = argparse.ArgumentParser()
parser.add_argument('--input-dir',
                    action='store',
                    nargs='+',
                    default='stdin',
                    type=str,
                    required=False,
                    help="directories where input files locate",
                    metavar='Diretories',
                    dest='dir')
parser.add_argument('--model',
                    action='store',
                    nargs=1,
                    type=str,
                    required=True,
                    help="path to the file where the model will be saved",
                    metavar="Model_path",
                    dest='mod')
parser.add_argument('--lc',
                    action='store_true',
                    default=False,
                    required=False,
                    help="lowercase",
                    dest='lc')
parser.add_argument('--morph',
                    action='store_true',
                    default=False,
                    required=False,
                    help="morphology",
                    dest='mor')
par = parser.parse_args()


def add_pair(first_word, second_word, data):
    first_word_data = data.pop(first_word, {})
    pair_freq = first_word_data.pop(second_word, 0)
    first_word_data.update({second_word: pair_freq + 1})
    data.update({first_word: first_word_data})


def parse_line(line, data, prev_word):
    words = re.findall(r"\w+", line)
    for cur_word in words:
        if prev_word[0] != "":
            add_pair(prev_word[0], cur_word, data[0])
        prev_word = [cur_word]


def morph_parse_line(line, data, prev_word, morph):
    words = re.findall(r"\w+", line)
    for cur_word in words:
        parse_cur_word = morph.parse(cur_word)
        for prev in prev_word:
            for word in parse_cur_word:
                if prev != "":
                    add_pair(prev, word.normal_form, data[0])
                    add_pair(prev, word.tag, data[1])
        prev_word = [word.normal_form for word in parse_cur_word]


def input(input_dir, data, lowercase, morphology):
    prev_word = [""]
    if morphology:
        morph = pymorphy2.MorphAnalyzer()
    if input_dir == 'stdin':
        for line in sys.stdin:
            if lowercase:
                line = line.lower()
            if morphology:
                morph_parse_line(line, data, prev_word, morph)
            else:
                parse_line(line, data, prev_word)
    else:
        for _dir in par.dir:
            files = os.listdir(_dir)
            for _file in files:
                f = open(_dir+'/'+_file, 'r')
                for line in f:
                    if lowercase:
                        line = line.lower()
                    if morphology:
                        morph_parse_line(line, data, prev_word, morph)
                    else:
                        parse_line(line, data, prev_word)
                f.close()


def output(output_file, data, morphology):
    f = open(output_file, 'w')
    if morphology:
        f.write("morph\n")
    i = 1
    for pairs in data:
        f.write(str(i) + "\n")
        for first_word in pairs:
            for second_word in pairs.get(first_word, {}):
                f.write(first_word + " " + str(second_word).replace(',', ' ') +
                        " " + str(pairs[first_word][second_word]) + "\n")
        i += 1
    f.close()


if par.mor:
    data = [{}, {}]
else:
    data = [{}]
input(par.dir, data, par.lc, par.mor)
output(par.mod[0], data, par.mor)
