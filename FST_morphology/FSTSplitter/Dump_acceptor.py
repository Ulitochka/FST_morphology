import sys
import time
import os


class DumpFST:
    """
    Класс для извлчения информации из дампа автомата.
    
    Порядок действий:
    
        Создание файлов с данными для компиляции автомата.
        
        Компиляция: 
                    fstcompile --isymbols=/.../FST_morphology/data/data_for_compil/syms/test_abc.syms
                               --osymbols=/.../FST_morphology/data/data_for_compil/syms/test_abc.syms
                               /.../FST_morphology/data/data_for_compil/txtfst/morpho.txtfst
                               /.../FST_morphology/fst/bin/morpho.fst
                               
        Статистика до минимизации:
                    fstinfo  /.../FST_morphology/fst/bin/morpho.fst > /.../FST_morphology/fst/stat/morpho.fst.info.txtfst
                    
        Детерминизация:
                    fstdeterminize /.../FST_morphology/fst/bin/morpho.fst /.../FST_morphology/fst/bin/morpho.determ.fst
                    
        Минимизация:
                    fstminimize /.../FST_morphology/fst/bin/morpho.determ.fst /.../FST_morphology/fst/bin/morpho.determ.min.fst
                    
        Стастика после минимизации:
                    fstinfo  /.../FST_morphology/fst/bin/morpho.determ.min.fst > /.../FST_morphology/fst/stat/morpho.determ.min.info.txtfst
                    
        Дамп:
                    fstprint 
                    --isymbols=/.../FST_morphology/data/data_for_compil/syms/test_abc.syms
                    --osymbols=/.../FST_morphology/data/data_for_compil/syms/test_abc.syms
                    /.../FST_morphology/fst/bin/morpho.determ.min.fst > /.../FST_morphology/fst/dump/morpho.determ.min.dump.info.txtfs
    
    """
    def __init__(self):
        self.states = []
        self.final_states = []
        self.dict_arcs = dict()
        self.tokens_from_fst = []
        self.file_path = os.path.split(os.path.abspath(__file__))[0]
        self.data_path = os.path.abspath(self.file_path + '/../fst/dump/lower_determ_min.info.txtfst')
        self.result_path = os.path.abspath(self.file_path + '/../data/data_from_fst/')

    def load_file(self):
        """
        Загрузка файла дампа.
        :return: 
        """

        f = open(self.data_path, encoding='utf8')
        for line in f.readlines():
            line_without_str = line.strip()
            if len(line_without_str.split('\t')) > 1:
                self.states.append(line_without_str.split('\t'))
            else:
                self.final_states.append(line_without_str.split('\t')[0])
        print('loading_data done.')

    def create_dictionary_arcs(self):
        """
        12	15	е	е
        12	27	ю	ю   ->   '12': [['15', 'е', 'е'], ['27', 'ю', 'ю'], ['24', 'я', 'я']]
        12	24	я	я
    
        :return:
        """

        for arcs in self.states:
            self.dict_arcs[arcs[0]] = self.dict_arcs.setdefault(arcs[0], list()) + [arcs[1:]]
        print('creating_dictionary_states done.')

    def reade(self):
        """
        Восстанавливаем слова из дампа вместе с их вершинами.
        Идем от финальных состояний.
        
        Пример:
            [
                [['0', '1', '3', '5', '7', '9', '12', '15'], ['а', 'й', 'к', 'а', 'н', 'ь', 'е']], 
                [['0', '1', '3', '5', '7', '9', '12', '27'], ['а', 'й', 'к', 'а', 'н', 'ь', 'ю']], 
                [['0', '1', '3', '5', '7', '9', '12', '24'], ['а', 'й', 'к', 'а', 'н', 'ь', 'я']], 
                [['0', '1', '3', '5', '7', '9', '12', '24', '26'], ['а', 'й', 'к', 'а', 'н', 'ь', 'я', 'м']], 
                [['0', '1', '3', '5', '7', '9', '12', '15', '27'], ['а', 'й', 'к', 'а', 'н', 'ь', 'е', 'м']], 
                [['0', '1', '3', '5', '7', '9', '11', '14', '27'], ['а', 'й', 'к', 'а', 'н', 'у', 'ш', 'у']], 
                [['0', '1', '3', '5', '7', '9', '12', '24', '26', '27'], ['а', 'й', 'к', 'а', 'н', 'ь', 'я', 'м', 'и']], 
                
            ]
        :return:
        """

        def searcher(dict_arcs):

            iter_results = dict()
            check_list = list()

            if result_dict[-1] == 'start':
                for key in dict_arcs:
                    if key == '0':
                        for sub_elements in dict_arcs[key]:
                            if sub_elements[0] in self.final_states:
                                self.tokens_from_fst.append([[key, sub_elements[0]], [sub_elements[-1]]])
                            iter_results[sub_elements[0]] = [[[key, sub_elements[0]], [sub_elements[-1]]]]
            if result_dict[-1] != 'start':
                for keys_part_of_words in result_dict[-1]:
                    if keys_part_of_words in dict_arcs.keys():

                        check_list.append(len(dict_arcs[keys_part_of_words]))

                        for sub_elements in dict_arcs[keys_part_of_words]:
                            if sub_elements[0] in iter_results.keys():
                                iter_results[sub_elements[0]] += [[[el for el in curr_element[0]] +
                                                                   [sub_elements[0]],
                                                                   [el for el in curr_element[1]] +
                                                                   [sub_elements[-1]]] for curr_element in
                                                                  result_dict[-1][keys_part_of_words]]
                            else:
                                iter_results[sub_elements[0]] = [[[el for el in curr_element[0]] +
                                                                  [sub_elements[0]],
                                                                  [el for el in curr_element[1]] +
                                                                  [sub_elements[-1]]] for curr_element in
                                                                 result_dict[-1][keys_part_of_words]]
                            if sub_elements[0] in self.final_states:
                                for sub_sub_elements in [[[el for el in curr_element[0]] +
                                                        [sub_elements[0]],
                                                        [el for el in curr_element[1]] +
                                                        [sub_elements[-1]]] for curr_element in
                                                         result_dict[-1][keys_part_of_words]]:
                                    self.tokens_from_fst.append(sub_sub_elements)

            print('check_list', sum(check_list))
            return iter_results

        def _cycle():
            if result_dict[-1] != dict():
                t1 = time.time()
                part_result = searcher(self.dict_arcs)
                result_dict.append(part_result)
                t2 = time.time()
                print('iterations count:', len(result_dict)-1, '/',
                      'time:', t2-t1, '/',
                      'elements count:', sum([len(element) for element in result_dict[-1].values()]), '/',
                      'words count:', len(self.tokens_from_fst))
                _cycle()
            else:
                pass

        result_dict = ['start']
        _cycle()
        print('reade done.')

    def save_tokens_with_arcs(self):
        """
        Сохраняем данные.
        Формат: 
            [
                ['айканье', '0-1-3-5-7-9-12-15'], 
                ['айканью', '0-1-3-5-7-9-12-27'], 
                ['айканья', '0-1-3-5-7-9-12-24']
            ]
        :return: 
        """

        result = list()
        words_with_arcs = list()
        for words_raw in self.tokens_from_fst:
            word = ','.join(words_raw[1]).replace(',', '')
            arcs = ','.join(words_raw[0]).replace(',', '-')
            result.append(word)
            words_with_arcs.append([word, arcs])
        print('words from fst count:', len(result))

        fileOut = self.result_path + '/words_with_arcs.txt'
        sys.stdout = open(fileOut, 'w', encoding='utf8', newline='')
        for el in words_with_arcs:
            correct_element = (str(el).replace('[', '')
                                      .replace(']', '')
                                      .replace("'", '')
                                      .replace(", ", ' '))
            print(correct_element)
        sys.stdout.close()


if __name__ == '__main__':
    dump_fst = DumpFST()
    dump_fst.load_file()
    dump_fst.create_dictionary_arcs()
    dump_fst.reade()
    dump_fst.save_tokens_with_arcs()
