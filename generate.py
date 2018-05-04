import random
import numpy
import pymorphy2
import sys
import argparse
import train


def download_model(input_file):
    """download model

    :param input_file: input file (string)
    :return: data (dict: {"lex": {...}...)
    """
    model = open(input_file, 'r')
    data = {}
    part_of_base = ""
    for line in model:
        if line == "lex\n":
            part_of_base = "lex"
            data.update({"lex": {}})
        elif line == "morph\n":
            part_of_base = "morph"
            data.update({"morph": {}})
        else:
            words = line.split()
            train.add_pair_of_words(words[0], ' '.join(words[1:-1]),
                                    int(words[-1]), data[part_of_base])
    model.close()
    return data


def print_word(word):
    """print word

    :param word: word (string)
    :return: nothing
    """
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


def choose_word(data):
    """choose a word from data

    :param data: data (dict: {word: frequency...})
    :return: word (string)
    """
    if data == {}:
        return ""
    else:
        new_words = [elem for elem in data]
        total = sum(data.values())
        probabilities = [elem / total for elem in data.values()]
        return numpy.random.choice(new_words, 1, probabilities)[0]


def generate_text(data, seed, length):
    """generate a text from data

    :param data: data (dict: {first_word: {second_word: frequency...}...})
    :param seed: first word (string)
    :param length: the number of words (int)
    :return: nothing
    """
    cur_word = seed
    print_word(cur_word)
    for i in range(length - 1):
        next_word = choose_word(data.get(cur_word, {}))
        if next_word == "":
            next_word = random.sample(data.keys(), 1)[0]
        print_word(next_word)
        cur_word = next_word
    print_word("\n")


def generate_text_with_morphology(data_lex, data_morph, seed, length):
    """generate a text from data using morphology

    :param data_lex: data (dict: {first_word: {second_word: frequency...}...})
    :param data_morph: data (dict: {first_word: {morph: frequency...}...})
    :param seed: first word (string)
    :param length: the number of words (int)
    :return: nothing
    """
    morph = pymorphy2.MorphAnalyzer()
    cur_word = seed
    print_word(cur_word)
    for i in range(length - 1):
        next_lex = choose_word(data_lex.get(cur_word, {}))
        if next_lex == "":
            next_word = random.sample(data_lex.keys(), 1)[0]
        else:
            next_lexemes = []
            for elem in morph.parse(next_lex):
                next_lexemes = next_lexemes + elem.lexeme
            morph_data = data_morph.get(cur_word, {})
            flag = False
            while (not flag) and morph_data != {}:
                next_morph = choose_word(morph_data)
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


def main():
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
    data = download_model(par.mod[0])
    if par.seed == "":
        seed = random.sample(data[1].keys(), 1)[0]
    else:
        seed = par.seed[0]
    if par.out[0] != "stdout":
        sys.stdout = open(par.out[0], 'w')
    if "morph" in data.keys():
        generate_text_with_morphology(data["lex"], data["morph"],
                                      seed, par.len[0])
    else:
        generate_text(data["lex"], seed, par.len[0])
    if par.out[0] != "stdout":
        sys.stdout.close()


if __name__ == "__main__":
    main()
