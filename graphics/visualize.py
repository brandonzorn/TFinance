import io
import pandas_datareader as pdr
import datetime
import matplotlib.pyplot as plt


# Функция создания графика акции, принимающая её индекс на рынке Yahoo Finance.
def do_stock_image(stock_name, delta=30):
    # Берём две даты: нынешнюю и 30 дней назад.
    current_date = datetime.datetime.today()
    p_date = datetime.datetime.today() - datetime.timedelta(days=delta)

    # Забираем данные из Yahoo Finance.
    stock = pdr.get_data_yahoo(stock_name,
                               start=p_date,
                               end=current_date)

    # Очищаем полотно от прошлых графов.
    plt.clf()

    # Создаем полотно с графиком.
    stock['Close'].plot(grid=True)
    plt.title(f'Курс акции {stock_name} за последние 30 дней', fontsize=14)
    plt.gca().set(ylabel='Price')

    # Записываем полученный график в байты и возвращаем полученное изображение.
    output = io.BytesIO()
    plt.savefig(output)
    contents = output.getvalue()
    return contents


def check_stock_prices(stock_name, delta=2) -> bool:
    current_date = datetime.datetime.today()
    p_date = datetime.datetime.today() - datetime.timedelta(days=delta)

    # Забираем данные из Yahoo Finance.
    stock = pdr.get_data_yahoo(stock_name,
                               start=p_date,
                               end=current_date)

    # Цены за последние 2 дня
    prev_price = stock['Close'][-2]
    curr_price = stock['Close'][-1]

    return curr_price > prev_price
