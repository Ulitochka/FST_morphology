import pickle
import os
import nltk
from pylab import *
from tqdm import tqdm
import csv
import random


WORD_LEN_THRESHOLD = [4, 5, 6, 7, 8]
WORDS_WITH_BORDER = []

file_path = os.path.split(os.path.abspath(__file__))[0]
words_with_arcs_data_path = os.path.abspath(file_path + '/../data/data_from_fst/words_with_arcs.txt')


def data_prepare(length_word):
    # Загружаем характеристики вершин (степени, средняя позиция, частота).
    # Загружаем слова с переходами и вершинами.
    with open(os.path.abspath(file_path + '/../data/raw_data/vertex/vertex_degree_pos_word_betw_info.pkl'), 'rb') as f:
        vertex_degree_pos_word_info = pickle.load(f)

    words_with_arcs = list()
    f = open(words_with_arcs_data_path, encoding='utf8')
    for line in f.readlines():
        line_without_str = line.strip()
        words_with_arcs.append(line_without_str.split(' '))
    words_with_arcs = words_with_arcs
    print('loading_files done.')

    # Из массива убираем короткие слова.
    print("count words_with_arcs before filter:", len(words_with_arcs))
    words_with_arcs = [words for words in words_with_arcs if len(words[0]) == length_word]
    print("count words_with_arcs after filter:", len(words_with_arcs))

    # Создания словаря вершин и их характеристик.
    dict_vertex = dict()
    for elements in vertex_degree_pos_word_info:
        dict_vertex[elements[0][1]] = dict_vertex.setdefault(elements[0][1], list()) + [[elements[0][0], elements[0][2]], elements[1], elements[2]]
    print("dictionary_vertex done.")

    # Добавления инф. о вершинах к словам.
    with tqdm(total=len(words_with_arcs)) as pbar:
        for words in words_with_arcs:
            words.append([[vertex, list()] for vertex in words[1].split('-')])
            for components in words[-1]:
                for vertex_key in dict_vertex:
                    if vertex_key == components[0]:
                        components[1].append(dict_vertex[vertex_key])
            pbar.update(1)

    file = os.path.abspath(file_path + '/../data/data_for_splitting/words_with_vertex_all_info_len_%s.pkl' % (str(length_word), ))
    f = open(file, 'wb')
    pickle.dump(words_with_arcs, f)
    f.close()


def splitter(length_word):
    """"
    ['аура', '0-32-310-1812-8472', [['0', []], 
                                    ['32', [[['1', '31'], ['1'], [176324]]]], 
                                    ['310', [[['1', '16'], ['2'], [2136]]]], 
                                    ['1812', [[['1', '7'], ['3'], [388]]]], 
                                    ['8472', [[['1', '3'], ['4'], [24]]]]]]
    ['ауре', '0-32-310-1812-8474', [['0', []], 
                                    ['32', [[['1', '31'],  ['1'], [176324]]]], 
                                    ['310', [[['1', '16'], ['2'], [2136]]]], 
                                    ['1812', [[['1', '7'], ['3'], [388]]]], 
                                    ['8474', [[['1', '3'], ['4'], [205]]]]]]
    ['ауру', '0-32-310-1812-8477', [['0', []], 
                                    ['32', [[['1', '31'],  ['1'], [176324]]]], 
                                    ['310', [[['1', '16'], ['2'], [2136]]]], 
                                    ['1812', [[['1', '7'], ['3'], [388]]]], 
                                    ['8477', [[['1', '1'], ['11'], [24]]]]]]
    ['ауры', '0-32-310-1812-135452', [['0', []], 
                                      ['32', [[['1', '31'], ['1'], [176324]]]], 
                                      ['310', [[['1', '16'], ['2'], [2136]]]], 
                                      ['1812', [[['1', '7'], ['3'], [388]]]], 
                                      ['135452', []]]]
    """

    VERTEX_MAX_FREQ_POSITION_IN_WORD = 3
    VERTEX_FREQ = 100

    with open(os.path.abspath(file_path + '/../data/data_for_splitting/words_with_vertex_all_info_len_%s.pkl' % (str(length_word), )), 'rb') as f:
        words_with_vertex_all_info = pickle.load(f)

    for tokens in words_with_vertex_all_info:
        vertex_split = []
        for index, vertex in enumerate(tokens[-1]):
            if vertex[-1] != []:
                # фильтр вершин;
                if index+1 != len(tokens[-1]):
                    if int(vertex[1][0][1][0]) >= VERTEX_MAX_FREQ_POSITION_IN_WORD:
                        if int(vertex[1][0][2][0]) >= VERTEX_FREQ:
                            # сохраняем вершину и ее частоту;
                            vertex_split.append((vertex[0], int(vertex[1][0][2][0])))
        # print(tokens, vertex_split, '\n')
        tokens.append(vertex_split)

    for words in words_with_vertex_all_info:
        symbols_with_vertex = list(zip(list(words[0]), list(nltk.bigrams(words[1].split('-')))))
        border_index = set()
        if words[-1] != []:
            # берем вершину с максимальной частотой;
            vertex_spl = [v for v in words[-1] if v[1] == max([vertex_split[1] for vertex_split in words[-1]])][0][0]
            for s_v in symbols_with_vertex:
                if vertex_spl == s_v[1][1]:
                    border_index.add(symbols_with_vertex.index(s_v)+1)

        if len(border_index) > 1:
            assert(1==0)

        for i in border_index:
            symbols_with_vertex.insert(i, ('|',))
        # print(words[0], ''.join([el[0] for el in symbols_with_vertex]), border_index)
        WORDS_WITH_BORDER.append([words[0], ''.join([el[0] for el in symbols_with_vertex])])

for i in WORD_LEN_THRESHOLD:
    # data_prepare(i)
    splitter(i)

random.shuffle(WORDS_WITH_BORDER)

columns_names = ["initial_token", "token_with_border"]
with open(os.path.abspath(file_path + '/../data/result/words_with_border.csv'), 'w', newline='') as csv_file:
    writer = csv.writer(csv_file, delimiter=',',  quotechar=' ', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(columns_names)
    for el in WORDS_WITH_BORDER:
        writer.writerow(el)
