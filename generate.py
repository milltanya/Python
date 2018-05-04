import random
import numpy
import pymorphy2
import sys
import argparse
import pickle


def add_word_to_text(word):
    """print word

    :param word: word (string)
    :return: nothing
    """
    if "text" not in dir(add_word_to_text):
        add_word_to_text.text = ""
    if "max" not in dir(add_word_to_text):
        add_word_to_text.max = 2000
    if word == "\n":
        print(add_word_to_text.text)
        add_word_to_text.text = ""
    else:
        if add_word_to_text.text != "":
            add_word_to_text.text += " "
        add_word_to_text.text += word
        if len(add_word_to_text.text) > add_word_to_text.max:
            print(add_word_to_text.text)
            add_word_to_text.text = ""


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


def generate_text(data, seed, length, paragraph):
    """generate a text from data

    :param data: data (dict: {first_word: {second_word: frequency...}...})
    :param seed: first word (string)
    :param length: the number of words (int)
    :param paragraph: the number of symbols in a paragraph (int)
    :return: nothing
    """
    cur_word = seed
    add_word_to_text.max = paragraph
    add_word_to_text(cur_word)
    for i in range(length - 1):
        next_word = choose_word(data.get(cur_word, {}))
        if next_word == "":
            next_word = random.sample(data.keys(), 1)[0]
        add_word_to_text(next_word)
        cur_word = next_word
    add_word_to_text("\n")


def generate_text_with_morphology(data_lex, data_morph, seed,
                                  length, paragraph):
    """generate a text from data using morphology

    :param data_lex: data (dict: {first_word: {second_word: frequency...}...})
    :param data_morph: data (dict: {first_word: {morph: frequency...}...})
    :param seed: first word (string)
    :param length: the number of words (int)
    :param paragraph: the number of symbols in a paragraph (int)
    :return: nothing
    """
    morph = pymorphy2.MorphAnalyzer()
    cur_word = seed
    add_word_to_text.max = paragraph
    add_word_to_text(cur_word)
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
        add_word_to_text(next_word)
        cur_word = next_word
    add_word_to_text("\n")


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
    parser.add_argument('--paragraph',
                        action='store',
                        nargs=1,
                        default=[1000],
                        type=int,
                        required=False,
                        help="the number of symbols in a paragraph",
                        dest='par')
    parser.add_argument('--output ',
                        action='store',
                        nargs=1,
                        default=['stdout'],
                        type=str,
                        help="path to the file where the text will locate",
                        dest='out')
    par = parser.parse_args()
    model = open(par.mod[0], 'rb')
    data = pickle.load(model)
    model.close()
    if par.seed == "":
        seed = random.sample(data["lex"].keys(), 1)[0]
    else:
        seed = par.seed[0]
    if par.out[0] != "stdout":
        sys.stdout = open(par.out[0], 'w')
    if "morph" in data.keys():
        generate_text_with_morphology(data["lex"], data["morph"],
                                      seed, par.len[0], par.par[0])
    else:
        generate_text(data["lex"], seed, par.len[0], par.par[0])
    if par.out[0] != "stdout":
        sys.stdout.close()


if __name__ == "__main__":
    main()
