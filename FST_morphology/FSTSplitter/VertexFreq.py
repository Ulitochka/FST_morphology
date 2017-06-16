# Количество вхождений вершин в кратчайшие пути между двумя вершинами.

import os
import pickle
from pprint import pprint
from collections import Counter
import sys
from tqdm import tqdm

class Betweenness:
    def __init__(self):
        self.file_path = os.path.split(os.path.abspath(__file__))[0]
        self.words_with_arcs_data_path = os.path.abspath(self.file_path + '/../data/data_from_fst//words_with_arcs.txt')
        self.vertex_unique_elements_data_path = os.path.abspath(self.file_path + '/../data/raw_data/vertex/')
        self.vertex_degree_pos_word_info = self.vertex_unique_elements_data_path + '/vertex_degree_pos_word_info.pkl'

        self.arcs_freq = None

    def create_arcs_words(self):
        """
        Загружаем массив слов с их переходами. Создаем словарь частот переходов.
        :return:
        """

        arcs = list()
        f = open(self.words_with_arcs_data_path, encoding='utf8')
        for line in f.readlines():
            line_without_str = line.strip()
            for elements in line_without_str.split(' ')[1].split('-'):
                arcs.append(elements)

        arcs_freq = Counter(arcs)

        print('dictionary_arcs:', len(arcs_freq))
        self.arcs_freq = arcs_freq


    def adding_betw_to_vertex(self):
        """
        Добавляем частоту вершин.
        :return:
        """

        with open(self.vertex_degree_pos_word_info, 'rb') as f:
            vertex_degree_pos_word_info = pickle.load(f)

        with tqdm(total=len(vertex_degree_pos_word_info)) as pbar:
            for elements_vertex in vertex_degree_pos_word_info:
                for elements_v_b in self.arcs_freq:
                    if elements_vertex[0][1] == elements_v_b:
                        elements_vertex[2].append(self.arcs_freq[elements_v_b])
                        pbar.update(1)

        pprint(vertex_degree_pos_word_info)

        file = self.vertex_unique_elements_data_path + '/vertex_degree_pos_word_betw_info.pkl'
        f = open(file, 'wb')
        pickle.dump(vertex_degree_pos_word_info, f)
        f.close()


if __name__ == '__main__':
    stat_vertex = Betweenness()
    stat_vertex.create_arcs_words()
    stat_vertex.adding_betw_to_vertex()
