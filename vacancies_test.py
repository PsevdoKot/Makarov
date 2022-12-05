import unittest
from vacancies import normalize_input_info, DataSet, InputConnect, Vacancy, Salary


class NormalizeInputTests(unittest.TestCase):
    def test_normal_input(self):
        self.assertEqual(normalize_input_info(["vacancies_medium.csv", "Оклад: 50000", "Опыт работы", "Да", "10",
                                              "Название, Опыт, Оклад, Компания, Название региона"]),
                                              "Нормализация прошла успешно")
    def test_empty_input(self):
        self.assertEqual(normalize_input_info(["vacancies_empty.csv", "Оклад: 50000", "Опыт работы", "Да", "10",
                                              "Название, Опыт, Оклад, Компания, Название региона"]),
                                              "Пустой файл")
    def test_wrong_filtering_parameter_1(self):
        self.assertEqual(normalize_input_info(["vacancies_medium.csv", "Оклад - 50000", "Опыт работы", "Да", "10",
                                              "Название, Опыт, Оклад, Компания, Название региона"]),
                                              "Формат ввода некорректен")
    def test_wrong_filtering_parameter_2(self):
        self.assertEqual(normalize_input_info(["vacancies_medium.csv", "Новизна: 50000", "Опыт работы", "Да", "10",
                                              "Название, Опыт, Оклад, Компания, Название региона"]),
                                              "Параметр поиска некорректен")
    def test_wrong_sorting_parameter(self):
        self.assertEqual(normalize_input_info(["vacancies_medium.csv", "Оклад: 50000", "Опыт труда", "Да", "10",
                                              "Название, Опыт, Оклад, Компания, Название региона"]),
                                              "Параметр сортировки некорректен")
    def test_wrong_reverse_sorting_parameter(self):
        self.assertEqual(normalize_input_info(["vacancies_medium.csv", "Оклад: 50000", "Опыт работы", "Как хочешь", "10",
                                              "Название, Опыт, Оклад, Компания, Название региона"]),
                                              "Порядок сортировки задан некорректно")

class CsvFilterTests(unittest.TestCase):
    dataSet = DataSet(None)
    def test_filter_empty_1(self):
        self.assertEqual(self.dataSet._csv_filter(""), "")

    def test_filter_empty_2(self):
        self.assertEqual(self.dataSet._csv_filter("  \t     "), "")

    def test_filter_normal_1(self):
        self.assertEqual(self.dataSet._csv_filter(
            "   Тестовое       сообщение     в   тестовое      тесто    в     тестовом    славии!!      "),
            "Тестовое сообщение в тестовое тесто в тестовом славии!!")

    def test_filter_normal_2(self):
        self.assertEqual(self.dataSet._csv_filter(
            "<p>В оптово-розничных холдинг требует программист 1С</p> <p><strong>"
             "Обязанности:</strong></p> <ul> <li>Поддержка и доработка конфигурации для мобильной платформы "
             "«1С Предприятие»</li> <li>Настройка и создание новых отчетов"),
            "В оптово-розничных холдинг требует программист 1С Обязанности: Поддержка и доработка конфигурации для "
             "мобильной платформы «1С Предприятие» Настройка и создание новых отчетов")

    def test_filter_normal_3(self):
        self.assertEqual(self.dataSet._csv_filter(
            "<p><strong>Наши задачи: </strong></p> <ul> <li>разработка программного обеспечения (общего назначения и "
             "производственного назначения);</li> <li>поддержка находящегося в эксплуатации программного обеспечения."
             "</li> </ul> <p><strong>Нам важно: </strong></p> <ul> <li>высшее, неоконченное высшее, "
             "среднее специальное образование;"),
            "Наши задачи: разработка программного обеспечения (общего назначения и производственного назначения); "
             "поддержка находящегося в эксплуатации программного обеспечения. Нам важно: высшее, неоконченное высшее, "
             "среднее специальное образование;")

    def test_filter_key_skills(self):
        self.assertEqual(self.dataSet._csv_filter("XML\nSQL\nAtlassian Jira\nSOAP\nREST\nXsd\nJSON\nAPI"),
            "XML__temp__SQL__temp__Atlassian Jira__temp__SOAP__temp__REST__temp__Xsd__temp__JSON__temp__API")


class CreatingVacancyListTest(unittest.TestCase):
    dataSet = DataSet(None)
    def test_normal_info(self):
        def compare_vacancies(vac1, vac2):
            return vac1.name == vac2.name and vac1.description == vac2.description and \
                   vac1.key_skills == vac2.key_skills and vac1.experience_id == vac2.experience_id and \
                   vac1.premium == vac2.premium and vac1.employer_name == vac2.employer_name and \
                   vac1.salary.salary_from == vac2.salary.salary_from and \
                   vac1.salary.salary_to == vac2.salary.salary_to and \
                   vac1.salary.salary_currency == vac2.salary.salary_currency and \
                   vac1.salary.salary_gross == vac2.salary.salary_gross and \
                   vac1.area_name == vac2.area_name and vac1.published_at == vac2.published_at

        vac_list = self.dataSet._create_vacancies(
            ["name", "description", "key_skills", "experience_id", "premium", "employer_name", "salary_from",
             "salary_to", "salary_gross", "salary_currency", "area_name", "published_at"],
            [["проф1", "опис1", "скил1__temp__скил2__temp__скил3", "10лет", "True",
              "Kvakvak", "200", "300", "False", "EUR", "Kuznetsk", "2020-05-31T17:32:31+0300"],
             ["проф2", "опис2", "скил4__temp__скил5__temp__скил6", "11лет", "False",
              "Lagala", "200", "300", "False", "USD", "Moskwak", "2021-05-31T17:32:31+0300"],
             ["проф3", "опис3", "скил6__temp__скил7__temp__скил8", "12лет", "True",
              "Hiffe", "200", "300", "True", "RUR", "Pitervak", "2022-05-31T17:32:31+0300"]])
        self.assertEqual(
            compare_vacancies(vac_list[0], Vacancy("проф1", "опис1", ["скил1", "скил2", "скил3"], "10лет", "True",
              "Kvakvak", Salary("200", "300", "False", "EUR"), "Kuznetsk", "2020-05-31T17:32:31+0300")), True)
        self.assertEqual(
            compare_vacancies(vac_list[1], Vacancy("проф2", "опис2", ["скил4", "скил5", "скил6"], "11лет", "False",
              "Lagala", Salary("200", "300", "False", "USD"), "Moskwak", "2021-05-31T17:32:31+0300")), True)
        self.assertEqual(
            compare_vacancies(vac_list[2], Vacancy("проф3", "опис3", ["скил6", "скил7", "скил8"], "12лет", "True",
              "Hiffe", Salary("200", "300", "True", "RUR"), "Pitervak", "2022-05-31T17:32:31+0300")), True)
        self.assertEqual(vac_list[1].key_skills, ["скил4", "скил5", "скил6"])

class InfoFormatterTests(unittest.TestCase):
    def test_normal_data_1(self):
        vac = Vacancy("Программ-аналитик", "Описание очень крутой и лучшей компании. Вот.",
                      "Программист,\nАналитик,\nАнализ", "moreThan6", "True", "ИнтелПроджект",
                      Salary("12000.0", "35000.0", "False", "KGS"), "Екатеринбург", "2022-05-31T17:32:31+0300")
        formatted_vac = InputConnect.info_formatter([vac])[0]

        self.assertEqual(formatted_vac.name, "Программ-аналитик")
        self.assertEqual(formatted_vac.description, "Описание очень крутой и лучшей компании. Вот.")
        self.assertEqual(formatted_vac.key_skills, "3#Программист,\nАналитик,\nАнализ")
        self.assertEqual(formatted_vac.experience_id, "Более 6 лет")
        self.assertEqual(formatted_vac.premium, "Да")
        self.assertEqual(formatted_vac.employer_name, "ИнтелПроджект")
        self.assertEqual(formatted_vac.salary.salary_from, "12 000")
        self.assertEqual(formatted_vac.salary.salary_to, "35 000")
        self.assertEqual(formatted_vac.salary.salary_currency, "Киргизский сом")
        self.assertEqual(formatted_vac.salary.salary_gross, "С вычетом налогов")
        self.assertEqual(formatted_vac.area_name, "Екатеринбург")
        self.assertEqual(formatted_vac.published_at, "2022-05-31T17:32:31+0300#31.05.2022")

    def test_normal_data_2(self):
        vac = Vacancy("Настоящий ценитель анализа", "Молодцом",
                      "Обычное программирование,\nОбычный аланиз,\nСтраптивая аналтика,\nУмение выходить из трудных ситуация",
                      "noExperience", "False", "VolodcomOrg",
                      Salary("12345.0", "987654.0", "True", "EUR"), "Кышма", "1999-06-27T12:49:59+0300")
        formatted_vac = InputConnect.info_formatter([vac])[0]

        self.assertEqual(formatted_vac.name, "Настоящий ценитель анализа")
        self.assertEqual(formatted_vac.description, "Молодцом")
        self.assertEqual(formatted_vac.key_skills, "4#Обычное программирование,\nОбычный аланиз,\nСтраптивая аналтика,\n"
              "Умение выходить из трудных ситуация")
        self.assertEqual(formatted_vac.experience_id, "Нет опыта")
        self.assertEqual(formatted_vac.premium, "Нет")
        self.assertEqual(formatted_vac.employer_name, "VolodcomOrg")
        self.assertEqual(formatted_vac.salary.salary_from, "12 345")
        self.assertEqual(formatted_vac.salary.salary_to, "987 654")
        self.assertEqual(formatted_vac.salary.salary_currency, "Евро")
        self.assertEqual(formatted_vac.salary.salary_gross, "Без вычета налогов")
        self.assertEqual(formatted_vac.area_name, "Кышма")
        self.assertEqual(formatted_vac.published_at, "1999-06-27T12:49:59+0300#27.06.1999")

    def test_big_key_skills_and_discription_data(self):
        vac = Vacancy("name", "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt "
            "ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi "
            "ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum "
            "dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident",
            "Поле с количеством навыков превышающее 100 символов должно обязательно, в любом "
            "случае и при любом раскладе сокращено до этих 100 символов, в первую очередь по причине правильности",
            "moreThan6", "True", "NANNASNF", Salary("10", "100", "False", "RUR"), "fdsfsdfsefes", "1999-06-27T12:49:59+0300#27.06.1999")
        formatted_vac = InputConnect.info_formatter([vac])[0]

        self.assertEqual(formatted_vac.key_skills, "1#Поле с количеством навыков превышающее 100 символов должно "
            "обязательно, в любом случае и при любом р...")
        self.assertEqual(formatted_vac.description, "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed "
            "do eiusmod tempor incididunt ut labore ...")

class InfoFilterTests(unittest.TestCase):
    inputConnect = InputConnect()
    def test_experience_filter(self):
        vac_1 = Vacancy(None, None, None, "Более 6 лет", None, None, None, None, None)
        vac_2 = Vacancy(None, None, None, "Нет опыта", None, None, None, None, None)
        vac_3 = Vacancy(None, None, None, "От 1 года до 3 лет", None, None, None, None, None)
        vac_4 = Vacancy(None, None, None, "От 3 до 6 лет", None, None, None, None, None)
        vac_5 = Vacancy(None, None, None, "От 1 года до 3 лет", None, None, None, None, None)
        vac_6 = Vacancy(None, None, None, "Более 6 лет", None, None, None, None, None)
        filt_vac_list = self.inputConnect.info_filter([vac_1, vac_2, vac_3, vac_4, vac_5, vac_6],
                                                      ["Опыт работы", "Более 6 лет"])
        self.assertEqual(filt_vac_list, [vac_1, vac_6])

    def test_salary_value_filter(self):
        vac_1 = Vacancy(None, None, None, None, None, None, Salary("12345", "987654", "Без вычета налогов", "Рубли"), None, None)
        vac_2 = Vacancy(None, None, None, None, None, None, Salary("5000", "10000", "С вычетом налогов", "Евро"), None, None)
        vac_3 = Vacancy(None, None, None, None, None, None, Salary("35000", "70000", "С вычетом налогов", "Рубли"), None, None)
        vac_4 = Vacancy(None, None, None, None, None, None, Salary("3000", "4500", "С вычетом налогов", "Доллары"), None, None)
        vac_5 = Vacancy(None, None, None, None, None, None, Salary("20000", "67000", "Без вычета налогов", "Рубли"), None, None)
        vac_6 = Vacancy(None, None, None, None, None, None, Salary("100000", "100100", "Без вычета налогов", "Манаты"), None, None)
        filt_vac_list = self.inputConnect.info_filter([vac_1, vac_2, vac_3, vac_4, vac_5, vac_6],
                                                      ["Оклад", "30000"])
        self.assertEqual(filt_vac_list, [vac_1, vac_5])

    def test_salary_currency_filter(self):
        vac_1 = Vacancy(None, None, None, None, None, None, Salary("12345", "987654", "Без вычета налогов", "Рубли"), None, None)
        vac_2 = Vacancy(None, None, None, None, None, None, Salary("5000", "10000", "С вычетом налогов", "Евро"), None, None)
        vac_3 = Vacancy(None, None, None, None, None, None, Salary("35000", "70000", "С вычетом налогов", "Рубли"), None, None)
        vac_4 = Vacancy(None, None, None, None, None, None, Salary("3000", "4500", "С вычетом налогов", "Доллары"), None, None)
        vac_5 = Vacancy(None, None, None, None, None, None, Salary("20000", "67000", "Без вычета налогов", "Рубли"), None, None)
        vac_6 = Vacancy(None, None, None, None, None, None, Salary("100000", "100100", "Без вычета налогов", "Манаты"), None, None)
        filt_vac_list = self.inputConnect.info_filter([vac_1, vac_2, vac_3, vac_4, vac_5, vac_6],
                                                      ["Идентификатор валюты оклада", "Доллары"])
        self.assertEqual(filt_vac_list, [vac_4])

    def test_area_name_filter(self):
        vac_1 = Vacancy(None, None, None, None, None, None, None, "Москва", None)
        vac_2 = Vacancy(None, None, None, None, None, None, None, "Санкт-Петербург", None)
        vac_3 = Vacancy(None, None, None, None, None, None, None, "Тюмень", None)
        vac_4 = Vacancy(None, None, None, None, None, None, None, "Подольск", None)
        vac_5 = Vacancy(None, None, None, None, None, None, None, "Москва", None)
        vac_6 = Vacancy(None, None, None, None, None, None, None, "Владивосток", None)
        filt_vac_list = self.inputConnect.info_filter([vac_1, vac_2, vac_3, vac_4, vac_5, vac_6],
                                                      ["Название региона", "Москва"])
        self.assertEqual(filt_vac_list, [vac_1, vac_5])

    def test_key_skills_filter(self):
        vac_1 = Vacancy(None, None, "9#C, Python, Ruby, C#, Java, PHP, HTML, CSS, Delphi", None, None, None, None, None, None)
        vac_2 = Vacancy(None, None, "10#C++, C, Python, Ruby, JavaScript, Java, PHP, CSS, Git, Delphi", None, None, None, None, None, None)
        vac_3 = Vacancy(None, None, "6#Python, C#, JavaScript, Java, Git, Delphi", None, None, None, None, None, None)
        vac_4 = Vacancy(None, None, "9#C++, C, Ruby, C#, JavaScript, PHP, HTML, CSS, Git", None, None, None, None, None, None)
        vac_5 = Vacancy(None, None, "5#C, Python, Ruby, Java, Delphi", None, None, None, None, None, None)
        vac_6 = Vacancy(None, None, "7#C++, C#, JavaScript, Java, PHP, HTML, CSS", None, None, None, None, None, None)
        filt_vac_list = self.inputConnect.info_filter([vac_1, vac_2, vac_3, vac_4, vac_5, vac_6],
                                                      ["Навыки", "Git"])
        self.assertEqual(filt_vac_list, [vac_2, vac_3, vac_4])

class InfoSorterTests(unittest.TestCase):
    inputConnect = InputConnect()
    def test_key_skills_sort(self):
        vac_1 = Vacancy(None, None, "10#C++, C, Python, Ruby, JavaScript, Java, PHP, CSS, Git, Delphi", None, None, None, None, None, None)
        vac_2 = Vacancy(None, None, "8#C++, Ruby, C#, JavaScript, PHP, HTML, CSS, Git", None, None, None, None, None, None)
        vac_3 = Vacancy(None, None, "5#C, Python, Ruby, Java, Delphi", None, None, None, None, None, None)
        vac_4 = Vacancy(None, None, "7#C++, C#, JavaScript, Java, PHP, HTML, CSS", None, None, None, None, None, None)
        vac_5 = Vacancy(None, None, "6#Python, C#, JavaScript, Java, Git, Delphi", None, None, None, None, None, None)
        vac_6 = Vacancy(None, None, "9#C, Python, Ruby, C#, Java, PHP, HTML, CSS, Delphi", None, None, None, None, None, None)
        sort_vac_list = self.inputConnect.info_sorter([vac_1, vac_2, vac_3, vac_4, vac_5, vac_6],
                                                      "Навыки", False)
        self.assertEqual(sort_vac_list, [vac_3, vac_5, vac_4, vac_2, vac_6, vac_1])

    def test_reverse_key_skills_sort(self):
        vac_1 = Vacancy(None, None, "10#C++, C, Python, Ruby, JavaScript, Java, PHP, CSS, Git, Delphi", None, None, None, None, None, None)
        vac_2 = Vacancy(None, None, "8#C++, Ruby, C#, JavaScript, PHP, HTML, CSS, Git", None, None, None, None, None, None)
        vac_3 = Vacancy(None, None, "5#C, Python, Ruby, Java, Delphi", None, None, None, None, None, None)
        vac_4 = Vacancy(None, None, "7#C++, C#, JavaScript, Java, PHP, HTML, CSS", None, None, None, None, None, None)
        vac_5 = Vacancy(None, None, "6#Python, C#, JavaScript, Java, Git, Delphi", None, None, None, None, None, None)
        vac_6 = Vacancy(None, None, "9#C, Python, Ruby, C#, Java, PHP, HTML, CSS, Delphi", None, None, None, None, None, None)
        sort_vac_list = self.inputConnect.info_sorter([vac_1, vac_2, vac_3, vac_4, vac_5, vac_6],
                                                      "Навыки", True)
        self.assertEqual(sort_vac_list, [vac_1, vac_6, vac_2, vac_4, vac_5, vac_3])

    def test_experience_sort(self):
        vac_1 = Vacancy(None, None, None, "Более 6 лет", None, None, None, None, None)
        vac_2 = Vacancy(None, None, None, "От 1 до 3 лет", None, None, None, None, None)
        vac_3 = Vacancy(None, None, None, "Без опыта", None, None, None, None, None)
        vac_4 = Vacancy(None, None, None, "Без опыта", None, None, None, None, None)
        vac_5 = Vacancy(None, None, None, "Более 6 лет", None, None, None, None, None)
        vac_6 = Vacancy(None, None, None, "От 4 до 6 лет", None, None, None, None, None)
        sort_vac_list = self.inputConnect.info_sorter([vac_1, vac_2, vac_3, vac_4, vac_5, vac_6],
                                                      "Опыт работы", False)
        self.assertEqual(sort_vac_list, [vac_3, vac_4, vac_2, vac_6, vac_1, vac_5])
    def test_reverse_salary_value_sort(self):
        vac_1 = Vacancy(None, None, None, None, None, None, Salary("10000", "25000", "С вычетом налогов", "Рубли"), None, None)
        vac_2 = Vacancy(None, None, None, None, None, None, Salary("2000", "3000", "Без вычетом налогов", "Доллары"), None, None)
        vac_3 = Vacancy(None, None, None, None, None, None, Salary("1300", "2400", "С вычетом налогов", "Евро"), None, None)
        vac_4 = Vacancy(None, None, None, None, None, None, Salary("78000", "110000", "Без вычетом налогов", "Манаты"), None, None)
        vac_5 = Vacancy(None, None, None, None, None, None, Salary("41000", "87000", "Без вычетом налогов", "Рубли"), None, None)
        vac_6 = Vacancy(None, None, None, None, None, None, Salary("33000", "37000", "С вычетом налогов", "Узбекский сум"), None, None)
        vac_7 = Vacancy(None, None, None, None, None, None, Salary("45000", "55000", "Без вычетом налогов", "Рубли"), None, None)
        sort_vac_list = self.inputConnect.info_sorter([vac_1, vac_2, vac_3, vac_4, vac_5, vac_6, vac_7],
                                                      "Оклад", True)
        self.assertEqual(sort_vac_list, [vac_4, vac_2, vac_3, vac_5, vac_7, vac_1, vac_6])

    def test_name_sorter(self):
        vac_1 = Vacancy("Кадровик", None, None, None, None, None, None, None, None)
        vac_2 = Vacancy("Программист", None, None, None, None, None, None, None, None)
        vac_3 = Vacancy("Ассистент младшего уборщика", None, None, None, None, None, None, None, None)
        vac_4 = Vacancy("Головорез", None, None, None, None, None, None, None, None)
        vac_5 = Vacancy("Аналитик", None, None, None, None, None, None, None, None)
        vac_6 = Vacancy("Верстальщик", None, None, None, None, None, None, None, None)
        vac_7 = Vacancy("Последователь культа высшего кода", None, None, None, None, None, None, None, None)
        vac_8 = Vacancy("Шифровальщик", None, None, None, None, None, None, None, None)
        sort_vac_list = self.inputConnect.info_sorter([vac_1, vac_2, vac_3, vac_4, vac_5, vac_6, vac_7, vac_8],
                                                      "Название", False)
        self.assertEqual(sort_vac_list, [vac_5, vac_3, vac_6, vac_4, vac_1, vac_7, vac_2, vac_8])


if __name__ == "__main__":
    unittest.main()
