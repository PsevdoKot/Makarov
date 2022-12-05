import csv
import re
import os
from collections import abc
from functools import cmp_to_key
from prettytable import PrettyTable
from prettytable import ALL


def normalize_input_info(input_info):
    """Нормализует входящую информацию от пользователя.

    Args:
        input_info (list[str | bool | list[str] | list[int]]): Входящая информация от пользователя

    Returns:
        string: Результат нормализации входящей информации
    """
    table_fields = ["Название", "Описание", "Навыки", "Опыт работы", "Премиум-вакансия", "Компания", "Оклад",
                    "Название региона", "Дата публикации вакансии", "Идентификатор валюты оклада", "None"]
    if os.stat(input_info[0]).st_size == 0:
        return "Пустой файл"
    if input_info[1] == '':
        input_info[1] = "None: None"
    temp = input_info[1].find(': ')
    if temp == -1:
        return "Формат ввода некорректен"
    input_info[1] = [input_info[1][:temp], input_info[1][temp + 2:]]
    if input_info[1][0] not in table_fields:
        return "Параметр поиска некорректен"
    if input_info[2] == '':
        input_info[2] = '№'
    elif input_info[2] not in table_fields:
        return "Параметр сортировки некорректен"
    if input_info[3] == 'Да':
        input_info[3] = True
    elif input_info[3] == 'Нет' or input_info[3] == '':
        input_info[3] = False
    else:
        return "Порядок сортировки задан некорректно"
    input_info[4] = list(map(lambda x: 0 if x == '' else int(x) - 1, input_info[4].split(' ')))
    if len(input_info[4]) == 1:
        input_info[4].append(10000)
    input_info[5] = input_info[5].split(', ')
    if input_info[5][0] == '':
        input_info[5] = table_fields[:9]
    input_info[5].insert(0, '№')
    return "Нормализация прошла успешно"


class Vacancy:
    """Класс для представления вакансии

    Attributes:
        name (str): Название вакансии
        description (str):  Описание вакансии
        key_skills (list[str] | str): Необходимые скиллы для вакансии
        experience_id (str): Необходимый опыт для вакансии
        premium (str): Является ли вакансия премиумной
        employer_name (str): Название компании
        salary (Salary): Величина оклада
        area_name (str): Название города
        published_at (str): Время публикации вакансии
    """
    def __init__(self, name, description, key_skills, experience_id, premium,
                 employer_name, salary, area_name, published_at):
        """Инициализирует объект Vacancy

        Args:
            name (str | None):
            description (str | None):
            key_skills (list[str] | str | None):
            experience_id (str | None):
            premium (str | None):
            employer_name (str | None):
            salary (Salary | None):
            area_name (str | None):
            published_at (str | None):
        """
        self.name = name
        self.description = description
        self.key_skills = key_skills
        self.experience_id = experience_id
        self.premium = premium
        self.employer_name = employer_name
        self.salary = salary
        self.area_name = area_name
        self.published_at = published_at


class Salary:
    """Класс для представления оклада

    Attributes:
        salary_from (str):
        salary_to (str):
        salary_gross (str):
        salary_currency (str):
    """
    def __init__(self, salary_from, salary_to, salary_gross, salary_currency):
        """Инициализирует объект Salary

        Args:
            salary_from (str):
            salary_to (str):
            salary_gross (any):
            salary_currency (str):
        """
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.salary_gross = salary_gross
        self.salary_currency = salary_currency

    def currency_to_rur(self):
        """Переводит верхнюю и нижнюю вилки оклада в рубли

        Returns:
            list[int,int]: Верхняя и нижняя вилки оклада в рублях
        """
        dic_currency_to_rub = {"Манаты": 35.68, "Белорусские рубли": 23.91, "Евро": 59.90, "Грузинский лари": 21.74,
                               "Киргизский сом": 0.76, "Тенге": 0.13, "Рубли": 1, "Гривны": 1.64, "Доллары": 60.66,
                               "Узбекский сум": 0.0055}
        return list(map(lambda x: int(x.replace(' ', '')) * dic_currency_to_rub[self.salary_currency],
                        (self.salary_from, self.salary_to)))


class DataSet:
    """Класс для получения информации из файла csv формата и базовой работы над данными из него

    Attributes:
        file_name (str): Название csv файла
        vacancies_objects (list[Vacancy]): Список вакансий полученных из csv файла
    """
    def __init__(self, file_name):
        """Инициализирует объект DataSet

        Args:
            file_name (str | None): Название файла
        """
        if (file_name == None):
            return
        (headers, info) = self._csv_reader(file_name)
        vacancies = self._create_vacancies(headers, info)
        self.file_name = file_name
        self.vacancies_objects = vacancies

    @staticmethod
    def _csv_reader(file_name):
        """Чтение csv файла.

        Args:
            file_name (str): Название csv файла для чтения

        Returns:
            tuple[str, str]: Результат чтения из csv файла в виде пары: лист с названиями столбцов,
                лист с основными данными
        """
        with open(file_name, encoding="utf-8-sig") as f:
            reader = [x for x in csv.reader(f)]
            headers = reader.pop(0)
            header_len = len(headers)
            info = list(filter(lambda data: '' not in data and len(data) == header_len, reader))
        return headers, info

    def _csv_filter(self, info_cell):
        """Удаление лишних символов из элемента словаря (html-тегов и т.д.)

        Args:
            info_cell (str): Ячейка csv файла

        Returns:
            str: Нормализованная ячейка csv файла
        """
        temp_info = "__temp__".join(info_cell.split("\n"))
        temp_info = re.sub(r"<[^<>]*>", "", temp_info)
        temp_info = re.sub(r"\s+", " ", temp_info)
        return str.strip(temp_info)

    def _create_vacancies(self, headers, info):
        """Преобразование прочитанных данных из csv файла в список вакансий, в котором каждой вакансии соответствует
            одна строка из csv файла

        Args:
            headers (list[str]): Названия столбцов csv файла
            info (list[list[str]]): Основные данные csv файла

        Returns:
            list[Vacancy]: Список строк в виде словарей
        """
        vacancies = []
        for info_row in info:
            info_list = list(map(lambda x: self._csv_filter(info_row[x]), range(len(headers))))
            salary = Salary(info_list[6], info_list[7], info_list[8], info_list[9])
            key_skills = info_list[2].split('__temp__')
            vacancy = Vacancy(info_list[0], info_list[1], key_skills, info_list[3], info_list[4],
                              info_list[5], salary, info_list[10], info_list[11])
            vacancies.append(vacancy)
        return vacancies


class InputConnect:
    @staticmethod
    def info_formatter(vacancies):
        """Нормализация данных в вакансиях

        Args:
            vacancies (list[Vacancy] | Vacancy): Список вакансий

        Returns:
            list[Vacancy] | Vacancy: Результат форматирования
        """
        def formatter_string_number(str_num):
            """Устранение дробных разделителей в строковом числе

            Args:
                str_num (str): Число для нормализации

            Returns:
                str: Результат форматирования числа
            """
            num = int(str_num if str_num.find('.') == -1 else str_num[:len(str_num) - 2])
            str_num_reverse = str(num)[::-1]
            return ' '.join(str_num_reverse[i:i + 3] for i in range(0, len(str_num_reverse), 3))[::-1]

        def formatter_experience_id(attr_value):
            """Преобразование оклада в нормированный вид

            Args:
                attr_value (Salary): Объект оклада

            Returns:
                Salary: Результат форматирования оклада
            """
            return dic_experience[attr_value]

        def formatter_salary(attr_value):
            """Преобразование оклада в нормированный вид

            Args:
                attr_value (Salary): Объект оклада

            Returns:
                Salary: Результат форматирования оклада
            """
            salary_from = formatter_string_number(attr_value.salary_from)
            salary_to = formatter_string_number(attr_value.salary_to)
            salary_gross = attr_value.salary_gross
            salary_gross = 'Без вычета налогов' if salary_gross == 'True' else 'С вычетом налогов' \
                if salary_gross == 'False' else salary_gross
            salary_currency = dic_currency[attr_value.salary_currency]
            return Salary(salary_from, salary_to, salary_gross, salary_currency)

        def formatter_published_at(attr_value):
            """Удаление времени и часового пояса из даты

            Args:
                attr_value (str): Значение времени публикации вакансии

            Returns:
                str: Отформатированная дата публикации
            """
            return f"{attr_value}#{attr_value[8:10]}.{attr_value[5:7]}.{attr_value[0:4]}"

        def formatter_premium(attr_value):
            """Преобразование значения премиумности вакансии, написанный на английском, в соответствующий
                русский вариант и запись в словарь результата

            Args:
                attr_value (str): Значение времени публикации вакансии

            Returns:
                str: Отформатированные значение премиумности
            """
            return 'Да' if attr_value == 'True' else 'Нет'

        def formatter_key_skills(attr_value):
            """Соединение листа скиллов в одну строку и обрезание по количеству

            Args:
                attr_value (list[str]): Значение времени публикации вакансии

            Returns:
                str: Отформатированные скиллы
            """
            if not isinstance(attr_value, str):
                value = '\n'.join(attr_value)
                value = formatter_standard_field_value(value)
                return f"{len(attr_value)}#{value}"
            line_count = attr_value.count('\n') + 1
            value = formatter_standard_field_value(attr_value)
            return f"{line_count}#{value}"

        def formatter_standard_field_value(attr_value):
            """Получение первых 100 символов строки

            Args:
                attr_value (str): Значение, которое нужно обрезать

            Returns:
                str: Отформатированная строка
            """
            return f"{attr_value[0:100]}..." if len(attr_value) > 100 else attr_value

        dic_experience = {"noExperience": "Нет опыта", "between1And3": "От 1 года до 3 лет",
                          "between3And6": "От 3 до 6 лет", "moreThan6": "Более 6 лет"}
        dic_currency = {"AZN": "Манаты", "BYR": "Белорусские рубли", "EUR": "Евро",
                        "GEL": "Грузинский лари", "KGS": "Киргизский сом", "KZT": "Тенге", "RUR": "Рубли",
                        "UAH": "Гривны", "USD": "Доллары", "UZS": "Узбекский сум"}
        dic_func = {"experience_id": formatter_experience_id, "salary": formatter_salary,
                    "published_at": formatter_published_at,
                    "premium": formatter_premium, "key_skills": formatter_key_skills,
                    "name": formatter_standard_field_value, "description": formatter_standard_field_value,
                    "employer_name": formatter_standard_field_value, "area_name": formatter_standard_field_value}

        for vacancy in vacancies:
            attrs = [a for a in dir(vacancy) if not a.startswith('__') and not callable(getattr(vacancy, a))]
            for attr in attrs:
                setattr(vacancy, attr, dic_func[attr](getattr(vacancy, attr)))
        return vacancies

    @staticmethod
    def info_filter(vacancies, filtering_parameter):
        """Фильтрация списка вакансий, соответствующих строкам csv файла

        Args:
            vacancies (list[Vacancy] | Vacancy): Список вакансий для фильтрации
            filtering_parameter (list[str,str]): Параметр фильтрации

        Returns:
            list[Vacancy] | Vacancy: Результат фильтрации
        """
        def filter_verbatim(vacancy, field_should):
            """Лексикографическое сравнивание значения из объекта вакансии с требуемым значением

            Args:
                vacancy (Vacancy): Объекта вакансии
                field_should (tuple[str, str]): Аттрибут объекта вакансии и требуемым значением

            Returns:
                bool: Результат сравнения
            """
            return getattr(vacancy, dic_naming[field_should[0]]) == field_should[1]

        def filter_key_skills(vacancy, field_should):
            """Cравнение значения скиллов из объекта вакансии с требуемым значением

            Args:
                vacancy (Vacancy): Объекта вакансии
                field_should (tuple[str, str]): Аттрибут объекта вакансии и требуемым значением

            Returns:
                bool: Результат сравнения
            """
            values_should = field_should[1].split(', ')
            key_skills = vacancy.key_skills[vacancy.key_skills.find('#') + 1:]\
                .replace(', ', '\n').replace('...', '\n').split('\n')
            return all(list(map(lambda value_should: value_should in key_skills, values_should)))

        def filter_salary(vacancy, field_should):
            """Сравнение значения оклада из объекта вакансии с требуемым значением

            Args:
                vacancy (Vacancy): Объекта вакансии
                field_should (tuple[str, str]): Аттрибут объекта вакансии и требуемым значением

            Returns:
                bool: Результат сравнения
            """
            salary = vacancy.salary
            return int(salary.salary_from.replace(' ', '')) <= int(field_should[1]) <= int(salary.salary_to
                                                                                           .replace(' ', ''))

        def filter_salary_currency(vacancy, field_should):
            """Сравнение значения валюты оклада из объекта вакансии с требуемым значением

            Args:
                vacancy (Vacancy): Объекта вакансии
                field_should (tuple[str, str]): Аттрибут объекта вакансии и требуемым значением

            Returns:
                bool: Результат сравнения
            """
            return vacancy.salary.salary_currency == field_should[1]

        def filter_published_at(vacancy, field_should):
            """Сравнение значения времени публикации из объекта вакансии с требуемым значением

            Args:
                vacancy (Vacancy): Объекта вакансии
                field_should (tuple[str, str]): Аттрибут объекта вакансии и требуемым значением

            Returns:
                bool: Результат сравнения
            """
            value = vacancy.published_at
            return value[value.find('#') + 1:] == field_should[1]

        dic_naming = {"Название": "name", "Описание": "description", "Опыт работы": "experience_id",
                      "Премиум-вакансия": "premium", "Компания": "employer_name", "Название региона": "area_name"}
        dic_filter = {"Название": filter_verbatim, "Описание": filter_verbatim, "Навыки": filter_key_skills,
                      "Опыт работы": filter_verbatim, "Премиум-вакансия": filter_verbatim, "Компания": filter_verbatim,
                      "Оклад": filter_salary, "Дата публикации вакансии": filter_published_at,
                      "Идентификатор валюты оклада": filter_salary_currency, "Название региона": filter_verbatim}

        return list(filter(lambda vacancy: filtering_parameter[0] == "None"
                                    or dic_filter[filtering_parameter[0]](vacancy, filtering_parameter), vacancies))

    @staticmethod
    def info_sorter(vacancies, sort_field, reverse_sort):
        """Сортировка списка вакансий, представляющих собой строки файла csv формата

        Args:
            vacancies (list[Vacancy]): Данные для сортировки
            sort_field (str): Параметр сортировки
            reverse_sort (bool): Сортировать ли в обратном порядке

        Returns:
            list[Vacancy]: Результат сортировки
        """
        def lexicographic_sorter(vacancy1, vacancy2):
            """Лексикографическое сравнение одного объекта вакансии с другим по параметру сортировки

            Args:
                vacancy1 (Vacancy): Первый объект вакансии для сравнения
                vacancy2 (Vacancy): Первый объект вакансии для сравнения

            Returns:
                int: Результат сравнения
            """
            return 1 if getattr(vacancy1, dic_naming[sort_field]) >= getattr(vacancy2, dic_naming[sort_field]) else -1

        def key_skills_sorter(vacancy1, vacancy2):
            """Сравнение одного объекта вакансии с другим по количеству навыков

            Args:
                vacancy1 (Vacancy): Первый объект вакансии для сравнения
                vacancy2 (Vacancy): Первый объект вакансии для сравнения

            Returns:
                int: Результат сравнения
            """
            (vacancy1_count, vacancy2_count) = list(map(
                lambda vacancy: int(vacancy.key_skills[:vacancy.key_skills.find('#')]), (vacancy1, vacancy2)))
            return vacancy1_count - vacancy2_count

        def experience_sorter(vacancy1, vacancy2):
            """Сравнение одного объекта вакансии с другим по количеству требуемых лет опыта

            Args:
                vacancy1 (Vacancy): Первый объект вакансии для сравнения
                vacancy2 (Vacancy): Первый объект вакансии для сравнения

            Returns:
                int: Результат сравнения
            """
            def find_first_num(row_value):
                """Получение первого числа в строке

                Args:
                    row_value (str): Строка для поиска

                Returns:
                    int: Результат поиска числа
                """
                row_num = list(filter(lambda char: char.isdigit(), row_value))
                return int(row_num[0]) if len(row_num) > 0 else 0

            (row1_num, row2_num) = list(map(
                lambda vacancy: find_first_num(vacancy.experience_id), (vacancy1, vacancy2)))
            return row1_num - row2_num

        def salary_sorter(vacancy1, vacancy2):
            """Сравнение одного объекта вакансии с другим по окладу

            Args:
                vacancy1 (Vacancy): Первый объект вакансии для сравнения
                vacancy2 (Vacancy): Первый объект вакансии для сравнения

            Returns:
                int: Результат сравнения
            """
            (vacancy1_salary, vacancy2_salary) = list(map(
                lambda vacancy: sum(vacancy.salary.currency_to_rur()) / 2, (vacancy1, vacancy2)))
            return vacancy1_salary - vacancy2_salary

        dic_naming = {"Название": "name", "Описание": "description", "Дата публикации вакансии": "published_at",
                      "Премиум-вакансия": "premium", "Компания": "employer_name", "Название региона": "area_name"}
        dic_sorter = {"Название": lexicographic_sorter, "Описание": lexicographic_sorter, "Навыки": key_skills_sorter,
                      "Опыт работы": experience_sorter, "Премиум-вакансия": lexicographic_sorter,
                      "Компания": lexicographic_sorter, "Оклад": salary_sorter, "Название региона": lexicographic_sorter,
                      "Дата публикации вакансии": lexicographic_sorter}

        vacancies.sort(key=cmp_to_key(dic_sorter[sort_field]), reverse=reverse_sort)

        return vacancies

    @staticmethod
    def print_vacancies(vacancies, start_end_nums, table_fields):
        """Печать талицы с вакансиями

        Args:
            vacancies (list[Vacancy]): Список вакансий, соответствующих строкам файла csv формата
            start_end_nums (list[int, int]): От и до какого номера включать вакансии в таблицу
            table_fields (list[str]): Название столбцов для вывода в таблицу
        """
        dic_naming = {"name": "Название", "description": "Описание", "key_skills": "Навыки",
                      "experience_id": "Опыт работы", "premium": "Премиум-вакансия", "employer_name": "Компания",
                      "salary": "Оклад", "area_name": "Название региона", "published_at": "Дата публикации вакансии"}
        info_table = PrettyTable(list(map(lambda key: dic_naming[key], dic_naming.keys())))
        for vacancy in vacancies:
            values = list(map(lambda attr: getattr(vacancy, attr), dic_naming.keys()))
            skills = values.pop(2)
            values.insert(2, skills[skills.find('#') + 1:])
            salary = values.pop(6)
            values.insert(6, f"{salary.salary_from} - {salary.salary_to}"
                             f" ({salary.salary_currency}) ({salary.salary_gross})")
            date = values.pop(8)
            values.insert(8, date[date.find('#') + 1:])
            info_table.add_row(values)
        info_table.add_autoindex('№')
        info_table.hrules = ALL
        info_table.align = 'l'
        info_table.max_width = 20
        print(info_table.get_string(start=start_end_nums[0], end=start_end_nums[1], fields=table_fields))


######################################################################################################################


def get_vacancies():
    """Получение информации с csv файла в виде таблицы с вакансиями на основе вводимых пользователем данных

    """
    input_requests = ["Введите название файла: ", "Введите параметр фильтрации: ", "Введите параметр сортировки: ",
                      "Обратный порядок сортировки (Да / Нет): ", "Введите диапазон вывода: ",
                      "Введите требуемые столбцы: "]
    input_info: list[str | bool | list[str] | list[int]] = [input(input_request) for input_request in input_requests]
    # input_info = ["vacancies.csv", "Навыки: Git, Linux", "", "", "",
    #               ""]
    normalize_result = normalize_input_info(input_info)
    if normalize_result != "Нормализация прошла успешно":
        return normalize_result
    data_set = DataSet(input_info[0])
    vacancies = data_set.vacancies_objects
    if len(vacancies) == 0:
        return "Нет данных"
    input_connect = InputConnect()
    formatted_info = input_connect.info_formatter(vacancies)
    filtered_info = input_connect.info_filter(formatted_info, input_info[1])
    if len(filtered_info) == 0:
        return "Ничего не найдено"
    if input_info[2] != '№':
        filtered_info = input_connect.info_sorter(filtered_info, input_info[2], input_info[3])
    input_connect.print_vacancies(filtered_info, input_info[4], input_info[5])
