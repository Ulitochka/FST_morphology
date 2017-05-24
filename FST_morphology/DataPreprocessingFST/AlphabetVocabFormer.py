import pickle
import sys
import glob
import os


class DataFormer:
    def __init__(self):

        self.file_path = os.path.split(os.path.abspath(__file__))[0]
        self.data_path = os.path.abspath(self.file_path + '/../data/data_for_compil/chars_pairs/')

        self.chunk_number_checking = 0
        self.final_states = list()
        self.alphabet = list()

    def indexer(self, file: str):
        """
        Добавление к парам символов порядковых индексов.
        :param file: 
        :return: 
        """

        with open(file, 'rb') as f:
            tokens = pickle.load(f)
            tokens_pairs_chars = [elements[1] for elements in tokens]

            # Добавляем 0 - показатель начала токена.
            tokens_pairs_chars = [[[[0], pairs[0], pairs[1]] if index == 0 else [[], pairs[0], pairs[1]]
                                   for index, pairs in enumerate(tokens)] for tokens in tokens_pairs_chars]

            # Добавляем символ f - показатель конца токена.
            tokens_pairs_chars = [[[pairs[0], pairs[1], pairs[2], 'f'] if index+1 == len(tokens) else pairs
                                   for index, pairs in enumerate(tokens)] for tokens in tokens_pairs_chars]

            # Все элементы группируются в массив.
            chars = [char for tokens in tokens_pairs_chars for char in tokens]
            # print('count chars:', len(chars))

            # Добавляем индекс паре символов.
            for i, blocks in enumerate(chars):
                if self.chunk_number_checking:
                    if blocks[0]:
                        blocks[0].append(i+self.chunk_number_checking+1)
                    else:
                        blocks[0] = [i+self.chunk_number_checking, i+self.chunk_number_checking+1]
                else:
                    if blocks[0]:
                        blocks[0].append(i + 1)
                    else:
                        blocks[0] = [i, i+1]
            self.chunk_number_checking = chars[-1][0][-1]
            # print('chunk number checking:', self.chunk_number_checking)
            return chars

    def file_finder(self):
        """
        Нахождение бинарных файлов.
        :return: 
        """

        os.chdir(self.data_path)
        list_files = glob.glob('*.*b')
        files_for_constructing = list()
        for files in list_files:
            string = self.data_path + "/" + files
            files_for_constructing.append(string)
        return files_for_constructing

    def form_txtfst_file(self):
        """
        Формирование файла txtfst с переходами и значениями дуг, финальными состояниями.
        :return: 
        """

        print('\n', 'form_txtfst_file starts ...')

        files_for_constructing = self.file_finder()

        file_out = os.path.abspath(self.file_path + '/../data/data_for_compil/txtfst/test.txtfst')
        sys.stdout = open(file_out, 'w', encoding='utf8', newline='')

        for j, files in enumerate(files_for_constructing):
            chars = self.indexer(files)

            # Запись в файл *.txtfst переходов и значений дуг.
            for ch_pair in chars:
                print(ch_pair[0][0], ch_pair[0][1], ch_pair[1], ch_pair[2])

            # Сохранение финальных состояний в массив.
            for el in chars:
                if 'f' in el:
                    self.final_states.append(el[0][-1])

            # Сохранение символов в массив.
            for letter_pair in chars:
                for letter in letter_pair:
                    if type(letter) == str:
                        if letter != 'f':
                            self.alphabet.append(letter)

        # Запись в файл *.txtfst финальных состояний.
        for states in self.final_states:
            print(states)

        sys.stdout.close()

    def form_syms_file(self):
        """
        Формирование файла алфавита.
        :return: 
        """

        self.alphabet = sorted(set(self.alphabet))
        self.alphabet = [[let, j] for j, let in enumerate(self.alphabet)]

        file_out = os.path.abspath(self.file_path + '/../data/data_for_compil/syms/test_abc.syms')
        sys.stdout = open(file_out, 'w', encoding='utf8', newline='')
        for el in self.alphabet:
            print(el[0], el[1])
        sys.stdout.close()

if __name__ == '__main__':
    data_former = DataFormer()
    data_former.form_txtfst_file()
    data_former.form_syms_file()
