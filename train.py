import re
import os
import pymorphy2
import sys
import argparse
import pickle
import collections


def parse_line(line, data):
    """
    Функция разбивает строку line на пары слов и записывает частоты в data.

    :param line: исходная строка (string)
    :param data: база слов и частот
                (defaultdict: {first_word: {second_word: frequency...}...})
    :return: None
    """
    words = re.findall(r"\w+", line)
    for cur_word in words:
        if "prev_word" in dir(parse_line) and parse_line.prev_word != "":
            data[parse_line.prev_word][cur_word] += 1
        parse_line.prev_word = cur_word


def parse_line_with_morph(line, data_lex, data_morph):
    """
    Функция разбивает строку line на пары слов, используя морфологию.
    В data_lex записываются пары инфинитовов слов, а в data_morph - пара
    инфинитив первого слова + морфологический разбор второго.

    :param line: исходная строка (string)
    :param data_lex: база слов в начальной форме и частот
                (defaultdict: {first_word: {second_word: frequency...}...})
    :param data_morph: база слов и возможных форм второго слова
                (defaultdict: {first_word: {morph: frequency...}...})
    :return: None
    """
    if "morph" not in dir(parse_line_with_morph):
        parse_line_with_morph.morph = pymorphy2.MorphAnalyzer()
    words = re.findall(r"\w+", line)
    for cur_word in words:
        parse_cur_word = parse_line_with_morph.morph.parse(cur_word)[0]
        if "prev_word" in dir(parse_line) and parse_line.prev_word != "":
            data_lex[parse_line.prev_word][parse_cur_word.normal_form] += 1
            data_morph[parse_line.prev_word][str(parse_cur_word.
                                                 tag).replace(',', ' ')] += 1
        parse_line.prev_word = parse_cur_word.normal_form


def dd():
    return collections.defaultdict(int)


def make_data_from_text(input_dir, lowercase, morphology):
    """
    Функция разбивает тексты в директории input_dir на строчки и
    записывает частоты слов, учитывая lowercase и morphology

    :param input_dir: директории, в которой лежат тексты (list)
    :param lowercase: нужно ли привести тексты к lowercase (bool)
    :param morphology: нужно ли использовать морфологию (bool)
    :return: база слов
                (defaultdict: {"lex": {first_word:
                            {second_word: frequency...}...}
                [, "morph": {first_word: {morph: frequency...}...}]})
    """
    data = {"lex": collections.defaultdict(dd)}
    if morphology:
        data.update({"morph": collections.defaultdict(dd)})
    files = []

    if input_dir == ['stdin']:
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
                                      data["morph"])
            else:
                parse_line(line, data["lex"])
    return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-dir',
                        nargs='+',
                        default=['stdin'],
                        type=str,
                        required=False,
                        help="directories where input files locate",)
    parser.add_argument('--model',
                        type=str,
                        required=True,
                        help="path to the file where the model will be saved",)
    parser.add_argument('--lc',
                        action='store_true',
                        default=False,
                        required=False,
                        help="lowercase",)
    parser.add_argument('--use_morph',
                        action='store_true',
                        default=False,
                        required=False,
                        help="morphology",)
    par = parser.parse_args()
    data = make_data_from_text(par.input_dir, par.lc, par.use_morph)
    model = open(par.model, 'wb')
    pickle.dump(data, model)
    model.close()


if __name__ == "__main__":
    main()
