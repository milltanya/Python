import re
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument('--input-dir',
                    action='store',
                    nargs='+',
                    default='',
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
                    help="lowercase input",
                    dest='lc')
par = parser.parse_args()


def parse_line(line):
    global par
    if par.lc:
        line = line.lower()
    global prev_word
    global data
    words = re.findall(r"\w+", line)
    for word in words:
        tmp1 = data.pop(prev_word, {})
        tmp2 = tmp1.pop(word, 0)
        tmp1.update({word: tmp2+1})
        data.update({prev_word: tmp1})
        prev_word = word

data = {}
prev_word = "BEGIN"
if par.dir == '':
    s = input()
    while s != '\0':
        parse_line(s)
        s = input()
else:
    for _dir in par.dir:
        files = os.listdir(_dir)
        for _file in files:
            f = open(_dir+'/'+_file, 'r')
            for line in f:
                parse_line(line)
            f.close()
word = "END"
tmp1 = data.pop(prev_word, {})
tmp2 = tmp1.pop(word, 0)
tmp1.update({word: tmp2+1})
data.update({prev_word: tmp1})

f = open(par.mod[0], 'w')
for word1 in data:
    for word2 in data.get(word1, {}):
        f.write(word1+" "+word2+" "+str(data[word1][word2])+"\n")
f.close()
