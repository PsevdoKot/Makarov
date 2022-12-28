# from vacancies import get_vacancies
# from statistics import CurrencyApiConnect
from statistics import get_statistics
from statistics import CurrencyApiConnect

def main_function():
    """Выбор типа анализа данных из csv-файла

    """
    main_input_request = "Выберите тип вывода: "
    # main_input_info = input(main_input_request)
    main_input_info = "Статистика"
    if main_input_info != "Вакансии" and main_input_info != "Статистика":
        print("Введён неправильный тип вывода")
        return
    # if main_input_info == "Вакансии":
    #     get_vacancies()
    # else:
    get_statistics()

def test():
    db = CurrencyApiConnect('currency_quotes.db')
    quotes = db.get_currency_quotes(('2003', '2022'))
    db.save_currency_quotes_in_db(quotes, ['USD','RUR','EUR','KZT','UAH','BYR'])
    cur_quotes = db.read_currency_quotes_from_db(['USD','RUR','EUR','KZT','UAH','BYR'])
    print(cur_quotes)

if __name__ == '__main__':
    # main_function()
    test()


# python -m cProfile -s cumtime main.py