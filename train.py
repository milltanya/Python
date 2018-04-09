import re
import argparse
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
par = parser.parse_args()


def parse_line(line, data, prev_word, lowercase):
    if par.lc:
        line = line.lower()
    words = re.findall(r"\w+", line)
    for cur_word in words:
        if prev_word != "":
            prev_word_data = data.pop(prev_word, {})
            pair_freq = prev_word_data.pop(cur_word, 0)
            prev_word_data.update({cur_word: pair_freq + 1})
            data.update({prev_word: prev_word_data})
        prev_word = cur_word


def input(input_dir, data, prev_word, lowercase):
    if input_dir == 'stdin':
        for line in sys.stdin:
            parse_line(line, data, prev_word, lowercase)
    else:
        for _dir in par.dir:
            files = os.listdir(_dir)
            for _file in files:
                f = open(_dir+'/'+_file, 'r')
                for line in f:
                    parse_line(line, data, prev_word, lowercase)
                f.close()


def output(output_file, data):
    f = open(output_file, 'w')
    for first_word in data:
        for second_word in data.get(first_word, {}):
            f.write(first_word + " " + second_word + " " +
                    str(data[first_word][second_word]) + "\n")
    f.close()


data = {}
prev_word = ""
input(par.dir, data, prev_word, par.lc)
output(par.mod[0], data)
