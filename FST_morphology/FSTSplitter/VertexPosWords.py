import pickle
import os
import glob
from pprint import pprint


class StatVertex:
    """
    Сбор информации о позициях вершин в словах и длин слов.
    """

    def __init__(self):
        self.file_path = os.path.split(os.path.abspath(__file__))[0]
        self.words_with_arcs_data_path = os.path.abspath(self.file_path + '/../data/data_from_fst//words_with_arcs.txt')
        self.words_with_arcs_parts_data_path = os.path.abspath(self.file_path + '/../data/raw_data/parts_vertex_transition_with_positions/')
        self.parts_vertex_pos_with_length_data_path = os.path.abspath(self.file_path + '/../data/raw_data/parts_vertex_transition_with_positions_with_length/')
        self.vertex_unique_elements_data_path = os.path.abspath(self.file_path + '/../data/raw_data/vertex/')

        self.vertex_unique_elements = None


    def chunking_vertex_massive(self, chunks=1000):
        """
        Создаем массив вершин с поизцииями вида:
            [
            [[вершина, позиция_в_слове], [...]]
            ]
        
        :return:
        """

        f = open(self.words_with_arcs_data_path, encoding='utf8')
        vertex_transition_with_positions = list()
        for line in f.readlines():
            line_without_str = line.strip()
            vertex_position = [[vertex, i] for i, vertex in enumerate(line_without_str.split(' ')[1].split('-'))]
            vertex_transition_with_positions.append(vertex_position)

        length_massive_words = len(vertex_transition_with_positions)
        chunking_size = int(round((length_massive_words / chunks), 0))
        part_vertex_transition_with_positions = ([vertex_transition_with_positions[i:i+chunking_size] for i in
                                range(0, len(vertex_transition_with_positions), chunking_size)])

        for i, element in enumerate(part_vertex_transition_with_positions):
            file = self.words_with_arcs_parts_data_path + '/%s_part_vertex_transition_with_positions.pkl'% i
            f = open(file, 'wb')
            pickle.dump(element, f)
            f.close()

        print('chunking_vertex_massive done.')

    def creating_massive_vertex_position_length_word(self, file, vertex):
        """
        Создание из каждого файла массива типа: 
            [вершина, [позиция_в_слове, длина_слова]]
        :param file:
        :return:
        """

        vertex_pos_length = list()
        with open(file, 'rb') as f:
            vertex_trans_with_pos = pickle.load(f)
        for elements in vertex_trans_with_pos:
            for sub_elements in elements:
                if sub_elements[0] != '0':
                    vertex.append(sub_elements[0])
                    vertex_pos_length.append([sub_elements[0], [sub_elements[1], len(elements)]])
        dictionary = dict()
        for components in vertex_pos_length:
            dictionary[components[0]] = dictionary.setdefault(components[0], list()) + [components[1]]
        return dictionary

    def vertex_position_word_length(self):
        """
        Создание массива вершин с указанием ее позиции и длины слова.
        :return:
        """

        os.chdir(self.words_with_arcs_parts_data_path)
        list_files = glob.glob('*.*pkl')
        files_for_constructing = list()
        vertex = list()

        pattern = self.words_with_arcs_parts_data_path
        for files in list_files:
            string = pattern + "/" + files
            files_for_constructing.append(string)

        for i, files in enumerate(files_for_constructing):
            result = self.creating_massive_vertex_position_length_word(files, vertex)
            file = self.parts_vertex_pos_with_length_data_path + '/%s_part_vertex_pos_with_length.pkl'% i
            f = open(file, 'wb')
            pickle.dump(result, f)
            f.close()

        vertex_unique_elements = [[v, [], [], []] for v in sorted(set(vertex))]

        file = self.vertex_unique_elements_data_path  + '/vertex_unique_elements.pkl'
        f = open(file, 'wb')
        pickle.dump(vertex_unique_elements, f)
        f.close()

        print('vertex_position_word_length done.')

    def get_pos_length_to_each_vertex(self, file, vertex_unique_elements):
        with open(file, 'rb') as f:
            vertex_trans_with_pos = pickle.load(f)
        for vertex_aim in vertex_unique_elements:
            for key_vertex in vertex_trans_with_pos:
                if vertex_aim[0] == key_vertex:
                    for elements in vertex_trans_with_pos[key_vertex]:
                        vertex_aim[1].append(str(elements[0]))
                        vertex_aim[2].append(str(elements[1]))
                        vertex_aim[3].append(str(elements))

    def group_vertex(self):
        """
        Из отдельных файлов собираем массив вида:
            [
             [вершина, [позиции], [длины токенов], [пары_позиция_длина_токена]],
            ]
        :return: 
        """

        with open(self.vertex_unique_elements_data_path  + '/vertex_unique_elements.pkl', 'rb') as f:
                vertex_unique_elements = pickle.load(f)
        print('vertex_unique_elements', len(vertex_unique_elements))

        os.chdir(self.parts_vertex_pos_with_length_data_path)
        list_files = glob.glob('*.*pkl')
        files_for_constructing = list()
        pattern = self.parts_vertex_pos_with_length_data_path

        for files in list_files:
            string = pattern + "/" + files
            files_for_constructing.append(string)

        ch = list()
        for i, files in enumerate(files_for_constructing):
            if i == 0:
                print(files)
                self.get_pos_length_to_each_vertex(files, vertex_unique_elements)
                ch.append(1)
                print('\rfiles count: ' + str(sum(ch)), end=' ')

        self.vertex_unique_elements = vertex_unique_elements

        file = self.vertex_unique_elements_data_path  + '/unique_vertex_with_positions_with_length_words.pkl'
        f = open(file, 'wb')
        pickle.dump(vertex_unique_elements, f)
        f.close()


if __name__ == '__main__':
    stat_vertex = StatVertex()
    stat_vertex.chunking_vertex_massive()
    stat_vertex.vertex_position_word_length()
    stat_vertex.group_vertex()

