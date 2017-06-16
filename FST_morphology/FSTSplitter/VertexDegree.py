import pickle
from pprint import pprint
import sys
import os


class DegreeVertex:
    """
    Статистика по степеням вершин автомата.
    Важно знать не только степень, но и символы переходов.
    
        10039---------30133
                и/и
                        
        30133---------9639
                л/л
                        
        30133--------19182
                щ/щ
      
        
        [
        1,                                          # входящая степень;
        [['10039', ['и', 'и']]],                    # входящие переходы;
        '30133',                                    # целевая вершина;
        [['9639', 'л', 'л'], ['19182', 'щ', 'щ']],  # исходящие переходы;
         2                                          # исходящая степень;
         ]

    """

    def __init__(self):
        self.file_path = os.path.split(os.path.abspath(__file__))[0]
        self.russian_morphology_aot_determ_min_dump_info = os.path.abspath(
            self.file_path + '/../fst/dump/russian_morphology_aot.determ.min.dump.info.txtfst')
        self.vertex = os.path.abspath(self.file_path + '/../data/raw_data/vertex/')

        self.fst_arcs = list()
        self.fst_final_states = list()

        self.THRESHOLD = 5

    def extract_vertex(self):
        """
        Извлечение вершин и финальных состояний.
        :return:
        """

        f = open(self.russian_morphology_aot_determ_min_dump_info, encoding='utf8')
        for line in f.readlines():
            line_without_str = line.strip()
            if len(line_without_str.split('\t')) > 1:
                self.fst_arcs.append(line_without_str.split('\t'))
            if len(line_without_str.split('\t')) == 1:
                self.fst_final_states.append(line_without_str.split('\t'))
        print('count vertex:', len(self.fst_arcs))
        print('count final states:', len(self.fst_final_states))

    def count_degree(self):
        """
        Вычисление исходящей, входящей степени для вершин.
        Пример:

            ['1753', '515', 'ж', 'ж'] 
            out_arcs: ('1753', ['515', 'ж', 'ж']) 
            in_arcs: ('515', ['1753', ['ж', 'ж']])
            
            1753-----------515
                    ж/ж
                            
            Мы считаем: у ноды 515 какое количество уникальных предшествующих переходов; 
                        у ноды 1753 какое количество уникальных последующих переходов.
                        
            Так как граф ненаправленный, то считаем в оба направления.
            
            Интепретируем как границу между различными морфемами. То есть: если у ноды 515 большое 
            количество уникальных предшествующих переходов - то возможно это граница морфем типа корня и аффикса, флексии;
            если у ноды 1753 большое количество уникальных предшествующих переходов - то возможно это 
            граница морфем типа префикса и корня;
            
            Далее формируем массив вида:
            
            ['30133', '9639', 'л', 'л']     ('30133', ['9639','л', 'л']) 
            ['30133', '19182', 'щ', 'щ'] -> ('30133', ['19182', 'щ', 'щ']) 
            ['10039', '30133', 'и', 'и']    ('10039', ['30133', 'и', 'и']) 
            
            
                    [
                    1,                                          # входящая степень;
            ->      [['10039', ['и', 'и']]],                    # входящие переходы;
                    '30133',                                    # целевая вершина;
                    [['9639', 'л', 'л'], ['19182', 'щ', 'щ']],  # исходящие переходы;
                     2                                          # исходящая степень;
                     ]
            
        :return: 
        """

        dict_states_out_arcs = dict()
        dict_states_in_arcs = dict()
        for elements in self.fst_arcs:
            dict_states_out_arcs[elements[0]] = dict_states_out_arcs.setdefault(elements[0], list()) + [elements[1:]]
            dict_states_in_arcs[elements[1]] = dict_states_in_arcs.setdefault(elements[1], list()) + [[elements[0], elements[2:]]]
        print('count dict_states_out_vertex:', len(dict_states_out_arcs))
        print('count dict_states_in_vertex:', len(dict_states_in_arcs))

        degree = list()
        for key_out in dict_states_out_arcs:
            for key_in in dict_states_in_arcs:
                if key_out == key_in:
                    degree.append(
                        [len(dict_states_in_arcs[key_in]),
                         dict_states_in_arcs[key_in],
                         key_in,
                         dict_states_out_arcs[key_out],
                         len(dict_states_out_arcs[key_out])]
                    )
        print('count degree elements (- state(0)):', len(degree))

        file = self.vertex + '/degree.pkl'
        f = open(file, 'wb')
        pickle.dump(degree, f)
        f.close()

    def out_result_binary(self, data, name_file):

        states_degree = zip([len(sorted(set([sub_letters[1][1][0] for sub_letters in elements[1]]))) for elements in
                             data], [elements[2] for elements in data],
                            [len(sorted(set([sub_letters[1] for sub_letters in elements[3]]))) for elements in
                             data])

        file = self.vertex + '%s' % name_file
        f = open(file, 'wb')
        pickle.dump(states_degree, f)
        f.close()

    def peak_and_plateau_strategy(self):
        """
        Стратегия пика и плато.
    
        Нестабильный элемент = степень с большим зн. - начало основы.
        Если есть аффикс, то его набор символов будет постоянным, а вот конечные / начальные гласные основ будут меняться.
        
        Сортировка по out_degree;
        Если количество уникальных символов превышает порог -> в массив states_with_peaks;
        Если количество уникальных символов равно -> в массив states_with_plateau;
    
        :return:
        """

        with open(self.vertex + '/degree.pkl', 'rb') as f:
            states_with_degree = pickle.load(f)

        states_with_peaks = list()
        for elements in states_with_degree:
            if len(sorted(set([sub_letters[1][1][0] for sub_letters in elements[1]]))) > self.THRESHOLD:
                states_with_peaks.append(elements)
            if len(sorted(set([sub_letters[1] for sub_letters in elements[3]]))) > self.THRESHOLD:
                states_with_peaks.append(elements)
        print('states_with_peaks:', len(states_with_peaks))

        states_with_plateau = list()
        for components in states_with_degree:
            if len(sorted(set([sub_letters[1][1][0] for sub_letters in components[1]]))) == \
                    len(sorted(set([sub_letters[1] for sub_letters in components[3]]))):
                states_with_plateau.append(components)
        print('states_with_plateau:', len(states_with_plateau))

        self.out_result_binary(states_with_peaks, '/states_with_peaks.pkl')



if __name__ == '__main__':
    degree_vertex = DegreeVertex()
    degree_vertex.extract_vertex()
    degree_vertex.count_degree()
    degree_vertex.peak_and_plateau_strategy()
