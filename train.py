import re
import os
import pymorphy2
import sys
import argparse
import pickle


def add_pair_of_words(first_word, second_word, frequency, data):
    """add a pair of word with frequency to database

    :param first_word: first word (string)
    :param second_word: second word (string)
    :param frequency: frequency (int)
    :param data: database (dict: {first_word: {second_word: frequency...}...})
    :return: nothing
    """
    first_word_data = data.pop(first_word, {})
    pair_freq = first_word_data.pop(second_word, 0)
    first_word_data.update({second_word: pair_freq + frequency})
    data.update({first_word: first_word_data})


def parse_line(line, data, prev_word):
    """parse a line and write pairs of words to data

    :param line: line to parse (string)
    :param data: data (dict: {first_word: {second_word: frequency...}...})
    :param prev_word: previous word (string)
    :return: nothing
    """
    words = re.findall(r"\w+", line)
    for cur_word in words:
        if prev_word[0] != "":
            add_pair_of_words(prev_word[0], cur_word, 1, data)
        prev_word[0] = cur_word


def parse_line_with_morph(line, data_lex, data_morph, prev_word):
    """parse a line using morphology

    :param line: line (string)
    :param data_lex: data (dict: {first_word: {second_word: frequency...}...})
    :param data_morph: data (dict: {first_word: {morph: frequency...}...})
    :param prev_word: previous_word (string)
    :param morph: morph file from PyMorphy2 (MorphAnalyzer)
    :return: nothing
    """
    if "morph" not in dir(parse_line_with_morph):
        parse_line_with_morph.morph = pymorphy2.MorphAnalyzer()
    words = re.findall(r"\w+", line)
    for cur_word in words:
        parse_cur_word = parse_line_with_morph.morph.parse(cur_word)
        for prev in prev_word:
            for word in parse_cur_word:
                if prev != "":
                    add_pair_of_words(prev, word.normal_form, 1, data_lex)
                    add_pair_of_words(prev, str(word.tag).replace(',', ' '),
                                      1, data_morph)
        prev_word = [word.normal_form for word in parse_cur_word]


def make_data_from_text(input_dir, lowercase, morphology):
    """making data from text

    :param input_dir: input directory (string)
    :param lowercase: make the text in lowercase (bool)
    :param morphology: make the text using morphology (bool)
    :return: data (list)
    """
    prev_word = [""]
    data = {"lex": {}}
    if morphology:
        data.update({"morph": {}})
    files = []

    if input_dir == 'stdin':
        files.append(sys.stdin)
    else:
        for directory in input_dir:
            for file in os.listdir(directory):
                files.append(open(directory+'/'+file, 'r'))
    for text in files:
        for line in text:
            if lowercase:
                line = line.lower()
            if morphology:
                parse_line_with_morph(line, data["lex"],
                                      data["morph"], prev_word)
            else:
                parse_line(line, data["lex"], prev_word)
    return data


def main():
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
    parser.add_argument('--use_morph',
                        action='store_true',
                        default=False,
                        required=False,
                        help="morphology",
                        dest='mor')
    par = parser.parse_args()
    data = make_data_from_text(par.dir, par.lc, par.mor)
    model = open(par.mod[0], 'wb')
    pickle.dump(data, model)
    model.close()


if __name__ == "__main__":
    main()
