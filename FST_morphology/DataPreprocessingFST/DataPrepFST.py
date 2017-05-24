import pickle
import os

file_name = 'test_tokens.txt'
file_path = os.path.split(os.path.abspath(__file__))[0]
data_path = os.path.abspath(file_path + '/../data/raw_data/text_data/' + file_name)


def loading_data(path: str):
    """
    Загрузка слов из текстового файла.
    :param path: 
    :return: массив строк.
    """

    print('Loading data starting ...')
    with open(path, 'r', encoding='utf-8') as train_text:
        train_text = train_text.read()
        sentences = train_text.lower().split('\n')
        return sorted(set(sentences))


def pairs_chars(forms_massive: list, chunking: bool):
    """
    Для каждой строки создается массив символов. 
    Пример:
        ['амасий', [['а', 'а'], ['м', 'м'], ['а', 'а'], ['с', 'с'], ['и', 'и'], ['й', 'й']]]
    Получившийся массив разбивается на n частей - отдельных файлов.
    :param forms_massive:
    :param chunking: 
    :return: 
    """

    print('Pairs chars starting ...')
    massive_pairs = list()
    for form in forms_massive:
        letter_pairs = [[letter, letter] for letter in form]
        massive_pairs.append([form, letter_pairs])

    if chunking:
        length_massive_words = len(massive_pairs)
        chunking_size = int(round((length_massive_words / 140), 0))
        part_morpho_for_fst = ([massive_pairs[i:i+chunking_size] for i in range(0, len(massive_pairs), chunking_size)])

        for i, element in enumerate(part_morpho_for_fst):
            file = os.path.abspath(file_path + '/../data/data_for_compil/chars_pairs/%s_part_morpho_for_fst.b' % i)
            f = open(file, 'wb')
            pickle.dump(element, f)
            f.close()
    else:
        file = os.path.abspath(file_path + '/../data/data_for_compil/chars_pairs/part_morpho_for_fst.b')
        f = open(file, 'wb')
        pickle.dump(massive_pairs, f)
        f.close()


tokens = loading_data(data_path)
pairs_chars(tokens, False)
