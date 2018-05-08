import re
import os
import pymorphy2
import sys
import argparse
import pickle


def add_pair_of_words(first_word, second_word, data):
    """добавить пару слов в базу

    :param first_word: первое слово (string)
    :param second_word: второе слово (string)
    :param data: база слов и частот
                (dict: {first_word: {second_word: frequency...}...})
    :return: nothing
    """
    if first_word not in data.keys():
        data.update({first_word: {}})
    if second_word not in data[first_word].keys():
        data[first_word].update({second_word: 0})
    data[first_word][second_word] += 1


def parse_line(line, data):
    """разбить строку на пары слов и добавить их в базу

    :param line: исходная строка (string)
    :param data: база слов и частот
                (dict: {first_word: {second_word: frequency...}...})
    :return: nothing
    """
    words = re.findall(r"\w+", line)
    for cur_word in words:
        if "prev_word" in dir(parse_line) and parse_line.prev_word != "":
            add_pair_of_words(parse_line.prev_word, cur_word, data)
        parse_line.prev_word = cur_word


def parse_line_with_morph(line, data_lex, data_morph):
    """разбить строку на пары слов и добавить их в базу с морфологией

    :param line: исходная строка (string)
    :param data_lex: база слов в начальной форме и частот
                (dict: {first_word: {second_word: frequency...}...})
    :param data_morph: база слов и возможных форм второго слова
                (dict: {first_word: {morph: frequency...}...})
    :return: nothing
    """
    if "morph" not in dir(parse_line_with_morph):
        parse_line_with_morph.morph = pymorphy2.MorphAnalyzer()
    words = re.findall(r"\w+", line)
    for cur_word in words:
        parse_cur_word = parse_line_with_morph.morph.parse(cur_word)[0]
        if "prev_word" in dir(parse_line) and parse_line.prev_word != "":
            add_pair_of_words(parse_line.prev_word,
                              parse_cur_word.normal_form, data_lex)
            add_pair_of_words(parse_line.prev_word,
                              str(parse_cur_word.tag).replace(',', ' '),
                              data_morph)
        parse_line.prev_word = parse_cur_word.normal_form


def make_data_from_text(input_dir, lowercase, morphology):
    """разбить тексты на пары слов и составить из них базу

    :param input_dir: директории, в которой лежат тексты (list)
    :param lowercase: нужно ли привести тексты к lowercase (bool)
    :param morphology: нужно ли использовать морфологию (bool)
    :return: база слов
                (dict: {"lex": {first_word: {second_word: frequency...}...}
                [, "morph": {first_word: {morph: frequency...}...}]})
    """
    data = {"lex": {}}
    if morphology:
        data.update({"morph": {}})
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
