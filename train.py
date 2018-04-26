import re
import os


def add_pair(first_word, second_word, data):
    """adda a pair of words into the data

    :param first_word: first word
    :param second_word: second word
    :param data: data
    :return: nothing
    """
    first_word_data = data[0].pop(first_word, {})
    pair_freq = first_word_data.pop(second_word, 0)
    first_word_data.update({second_word: pair_freq + 1})
    data[0].update({first_word: first_word_data})


def parse_line(line, data, prev_word):
    """parse a line

    :param line: line to parse
    :param data: data
    :param prev_word: previous word
    :return: nothing
    """
    words = re.findall(r"\w+", line)
    for cur_word in words:
        if prev_word[0] != "":
            add_pair(prev_word[0], cur_word, data)
        prev_word[0] = cur_word


def morph_parse_line(line, data, prev_word, morph):
    """parse a line using morphology

    :param line: line
    :param data: data
    :param prev_word: previous_word
    :param morph: morph file from PyMorphy2
    :return: nothing
    """
    import pymorphy2
    words = re.findall(r"\w+", line)
    for cur_word in words:
        parse_cur_word = morph.parse(cur_word)
        for prev in prev_word:
            for word in parse_cur_word:
                if prev != "":
                    add_pair(prev, word.normal_form, data)
                    add_pair(prev, word.tag, [data[1]])
        prev_word = [word.normal_form for word in parse_cur_word]


def input(input_dir, data, lowercase, morphology):
    """making a data from text

    :param input_dir: input directory
    :param data: data
    :param lowercase: make the text in lowercase or not
    :param morphology: using morphology or not
    :return: nothing
    """
    prev_word = [""]
    if morphology:
        import pymorphy2
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
        for _dir in input_dir:
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
    """write the base to the model

    :param output_file: output file
    :param data: data
    :param morphology: if morphology is used
    :return: nothing
    """
    f = open(output_file, 'w')
    i = 1
    for pairs in data:
        if i == 1:
            f.write("lex\n")
        elif i == 2:
            f.write("morph\n")
        for first_word in pairs:
            for second_word in pairs.get(first_word, {}):
                f.write(first_word + " " + str(second_word).replace(',', ' ') +
                        " " + str(pairs[first_word][second_word]) + "\n")
        i += 1
    f.close()


def main():
    import argparse
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
    if par.mor:
        data = [{}, {}]
    else:
        data = [{}]
    input(par.dir, data, par.lc, par.mor)
    output(par.mod[0], data, par.mor)


if __name__ == "__main__":
    main()
