import random
import numpy
import pymorphy2
import sys
import argparse
import pickle


def add_word_to_text(word):
    """добавить слово к тексту, если текст размером достиг максимума, вывести его

    :param word: слово (string)
    :return: nothing
    """
    if "text" not in dir(add_word_to_text):
        add_word_to_text.text = ""
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
    """выбрать следующее слово (или разбор) из базы

    :param data: база (dict: {word: frequency...})
    :return: word (string)
    """
    if data == {}:
        return ""
    else:
        return numpy.random.choice(list(data.keys()), 1,
                                   list(data.values()))[0]


def count_probabilities(data):
    """посчитать вероятности для каждой пары слов. Они запишутся вместо частот

    :param data: база (dict: {first_word: {second_word: frequency...}...})
    :return: nothing
    """
    for first_word in data.keys():
        total = sum(data[first_word].values())
        for second_word in data[first_word].keys():
            data[first_word][second_word] /= total


def generate_text(data, seed, length, paragraph):
    """сгенерировать текст из слов в базе

    :param data: база (dict: {first_word: {second_word: frequency...}...})
    :param seed: первое слово (string)
    :param length: количество слов в тексте (int)
    :param paragraph: максимальное количество символов в абзаце (int)
    :return: nothing
    """
    cur_word = seed
    count_probabilities(data)
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
    """сгенерировать текст из слов в базе

    :param data_lex: база слов в начальной форме
                (dict: {first_word: {second_word: frequency...}...})
    :param data_morph: база слов и возможных форм второго слова
                (dict: {first_word: {morph: frequency...}...})
    :param seed: первое слово (string)
    :param length: количество слов в тексте (int)
    :param paragraph: максимальное количество символов в абзаце (int)
    :return: nothing
    """
    morph = pymorphy2.MorphAnalyzer()
    cur_word = seed
    count_probabilities(data_lex)
    count_probabilities(data_morph)
    add_word_to_text.max = paragraph
    add_word_to_text(cur_word)
    for i in range(length - 1):
        next_inf = choose_word(data_lex.get(cur_word, {}))
        if next_inf == "":
            next_word = random.sample(data_lex.keys(), 1)[0]
        else:
            next_lexemes = []
            for elem in morph.parse(next_inf):
                next_lexemes.append(elem.lexeme)
            morph_data = data_morph.get(cur_word, {})
            found = False
            while (not found) and morph_data != {}:
                next_morph = choose_word(morph_data)
                next_morphemes = next_morph.split()
                for lexeme in next_lexemes:
                    found = True
                    for morpheme in next_morphemes:
                        if morpheme not in lexeme.tag:
                            found = False
                            break
                    if found:
                        next_word = lexeme.word
                        break
                morph_data.pop(next_morph, {})
            if not found:
                next_word = next_inf
        add_word_to_text(next_word)
        cur_word = next_word
    add_word_to_text("\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model',
                        type=str,
                        required=True,
                        help="path to the file where the model locates")
    parser.add_argument('--seed',
                        default='',
                        type=str,
                        help="first word")
    parser.add_argument('--length',
                        type=int,
                        required=True,
                        help="length")
    parser.add_argument('--paragraph',
                        default=[1000],
                        type=int,
                        required=False,
                        help="the number of symbols in a paragraph")
    parser.add_argument('--output',
                        default=['stdout'],
                        type=str,
                        help="path to the file where the text will locate")
    par = parser.parse_args()
    model = open(par.model, 'rb')
    data = pickle.load(model)
    model.close()
    if par.seed == "":
        seed = random.sample(data["lex"].keys(), 1)[0]
    else:
        seed = par.seed
    if par.output != "stdout":
        sys.stdout = open(par.output, 'w')
    if "morph" in data.keys():
        generate_text_with_morphology(data["lex"], data["morph"],
                                      seed, par.length, par.paragraph)
    else:
        generate_text(data["lex"], seed, par.length, par.paragraph)
    if par.output != "stdout":
        sys.stdout.close()


if __name__ == "__main__":
    main()
