import os
import sys
import pickle
from pprint import pprint


class DegreeVertexStat:
    """
    Статистика по вершинам и их степеням.
    Статиска по вершинам и символам перходов.
    """
    def __init__(self, option='count_degree'):
        self.file_path = os.path.split(os.path.abspath(__file__))[0]
        self.vertex = os.path.abspath(self.file_path + '/../data/raw_data/vertex/')
        self.vertex_stata_data_path = os.path.abspath(self.file_path + '/../data/raw_data/vertex_stata/')
        with open(self.vertex + '/degree.pkl', 'rb') as f:
            states_with_degree = pickle.load(f)
        self.states_with_degree_sorted = sorted(states_with_degree, key=lambda x: int(x[2]), reverse=True)

        if option == 'count_degree':
            self.count_degree_info()
        elif option == 'letters_degree':
            self.letters_degree_info()
        elif option == 'count_letters_degree':
            self.count_letters_degree_info()

    def count_degree_info(self):
        """        
        [
        1,                                          # входящая степень;
        [['10039', ['и', 'и']]],                    # входящие переходы;
        '30133',                                    # целевая вершина;
        [['9639', 'л', 'л'], ['19182', 'щ', 'щ']],  # исходящие переходы;
         2                                          # исходящая степень;
         ]
         
         ==>
         
           1898          135451               2
            389          135450               5
             95          135449               1
         
        :return: 
        """

        fileOut = self.vertex_stata_data_path + '/count_degree_info_out_sort.txt'
        sys.stdout = open(fileOut, 'w', encoding='utf8', newline='')
        fmt1 = '%50s'
        print(fmt1 % (('-' * 50,) * 1))
        fmt = '%15s %15s %15s'
        print(fmt % ('Indegree count', 'aim arc', 'Outdegree count'))
        print(fmt % (('-' * 15,) * 3))

        count_degree = sorted(self.states_with_degree_sorted, key=lambda x: x[-1], reverse=True)

        for values in zip([elements[0] for elements in count_degree],
                          [elements[2] for elements in count_degree],
                          [elements[-1] for elements in count_degree]):
            print(fmt % values)
        print(fmt1 % (('-' * 50,) * 1))
        sys.stdout.close()

    def letters_degree_info(self):
        """        
        [
        1,                                          # входящая степень;
        [['10039', ['и', 'и']]],                    # входящие переходы;
        '30133',                                    # целевая вершина;
        [['9639', 'л', 'л'], ['19182', 'щ', 'щ']],  # исходящие переходы;
         2                                          # исходящая степень;
         ]
         
        ==> 
        
        ['и']  30133 ['л', 'щ']

        :return: 
        """

        fileOut = self.vertex_stata_data_path + '/letters_degree_info.txt'
        sys.stdout = open(fileOut, 'w', encoding='utf8', newline='')
        fmt1 = '%50s'
        print(fmt1 % (('-' * 210,) * 1))
        fmt = '%90s %20s %100s'
        print(fmt % ('Indegree symbols', 'aim arc', 'Outdegree symbols'))
        print(fmt % ('-' * 90, '-' * 20, '-' * 100))
        for values in zip([
            sorted(set([sub_letters[1][1][0] for sub_letters in elements[1]])) for elements in self.states_with_degree_sorted],
                [elements[2] for elements in self.states_with_degree_sorted],
            [sorted(set([sub_letters[1] for sub_letters in elements[3]])) for elements in self.states_with_degree_sorted]):
            print(fmt % values)
        print(fmt1 % (('-' * 210,) * 1))
        sys.stdout.close()

    def count_letters_degree_info(self):
        """
        [
        1,                                          # входящая степень;
        [['10039', ['и', 'и']]],                    # входящие переходы;
        '30133',                                    # целевая вершина;
        [['9639', 'л', 'л'], ['19182', 'щ', 'щ']],  # исходящие переходы;
         2                                          # исходящая степень;
         ]
         
        ==> 
        
        1  30133 2
        
        :return: 
        """

        count_letters = [
            [len(sorted(set([sub_letters[1][1][0] for sub_letters in el[1]]))),
             el[2],
             len(sorted(set([sub_letters[1] for sub_letters in el[3]])))]
            for el in self.states_with_degree_sorted]
        count_letters = sorted(count_letters, key=lambda x: x[0], reverse=True)

        fileOut = self.vertex_stata_data_path + '/count_letters_degree_info_in_sort.txt'
        sys.stdout = open(fileOut, 'w', encoding='utf8', newline='')
        fmt1 = '%50s'
        print(fmt1 % (('-' * 50,) * 1))
        fmt = '%15s %15s %15s'
        print(fmt % ('Indegree symbols', 'aim arc', 'Outdegree symbols'))
        print(fmt % (('-' * 15,) * 3))

        for values in zip([elements[0] for elements in count_letters],
                          [elements[1] for elements in count_letters],
                          [elements[2] for elements in count_letters]):
            print(fmt % values)
        print(fmt1 % (('-' * 50,) * 1))
        sys.stdout.close()

if __name__ == '__main__':
    degree_vertex_stat = DegreeVertexStat(option='count_degree')
