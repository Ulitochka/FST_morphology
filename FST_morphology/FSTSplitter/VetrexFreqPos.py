import pickle
import os
from collections import Counter
from tqdm import tqdm
from pprint import pprint


class DataForMorphoSplit:

    def __init__(self, option='count_degree'):
        self.file_path = os.path.split(os.path.abspath(__file__))[0]
        self.vertex = os.path.abspath(self.file_path + '/../data/raw_data/vertex/')
        self.vertex_stata_data_path = os.path.abspath(self.file_path + '/../data/raw_data/vertex_stata/')
        self.vertex_unique_elements_data_path = os.path.abspath(self.file_path + '/../data/raw_data/vertex/')

        self.vertex_let_deg = []
        self.loading_data_vertex_degrees()
        self.adding_to_vertex_word_position_info()

    def loading_data_vertex_degrees(self):
        """
        Формируем массив вида: 
            [
             [['1', '90736', '1'], [], []],
            ]
        :return: 
        """

        file = self.vertex_stata_data_path + '/count_letters_degree_info_in_sort.txt'
        f = open(file)
        for line in f.readlines():
            line_without_str = line.strip()
            if len(' '.join(line_without_str.split()).split(' ')) == 3:
                self.vertex_let_deg.append([' '.join(line_without_str.split()).split(' '), list(), list()])
        print('vertex_degrees complete. count:', len(self.vertex_let_deg))

    def adding_to_vertex_word_position_info(self):
        """
        Добавление данных о самой частотной позиции вершины в слове.
        :return:
        """

        with open(self.vertex_unique_elements_data_path + '/unique_vertex_with_positions_with_length_words.pkl', 'rb') as f:
            unique_vertex_with_positions_with_length_words = pickle.load(f)

        unique_vertex_with_positions_with_length_words = {el[0]: el[1] for el in unique_vertex_with_positions_with_length_words}

        with tqdm(total=len(self.vertex_let_deg)) as pbar:
            for vert in self.vertex_let_deg:
                for elements in unique_vertex_with_positions_with_length_words:
                    if vert[0][1] == elements:
                        dict_pos = Counter(unique_vertex_with_positions_with_length_words[elements])
                        vert[1].append(sorted(list(dict_pos.items()), key=lambda x: x[1], reverse=True)[0][0])
                        pbar.update(1)

        pprint(self.vertex_let_deg)

        file = self.vertex_unique_elements_data_path + '/vertex_degree_pos_word_info.pkl'
        f = open(file, 'wb')
        pickle.dump(self.vertex_let_deg, f)
        f.close()

if __name__ == '__main__':
    morph_split = DataForMorphoSplit()
