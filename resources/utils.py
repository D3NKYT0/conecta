import datetime
import platform
import socket
import re
import uuid
import psutil
import logging

import matplotlib.pyplot as plt


def base36encode(number):
    base36, sign, alphabet = str(), str(), '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    if number < 0:
        sign = '-'
        number = -number
    if 0 <= number < len(alphabet):
        return sign + alphabet[number]
    while number != 0:
        number, i = divmod(number, len(alphabet))
        base36 = alphabet[i] + base36
    return sign + base36


def create_code():
    actual_datetime = datetime.datetime.now()
    actual_datetime = actual_datetime.strftime("1%d%m%y%H%M%S%f")
    return str(base36encode(int(actual_datetime)))


def getSystemInfo():
    try:
        info={}
        info['platform']=platform.system()
        info['platform-release']=platform.release()
        info['platform-version']=platform.version()
        info['architecture']=platform.machine()
        info['hostname']=socket.gethostname()
        info['ip-address']=socket.gethostbyname(socket.gethostname())
        info['mac-address']=':'.join(re.findall('..', '%012x' % uuid.getnode()))
        info['processor']=platform.processor()
        info['ram']=str(round(psutil.virtual_memory().total / (1024.0 **3)))+" GB"
        return info
    except Exception as e:
        return logging.exception(e)


def create_graphics(x_data: list, y_data: list, second_data: list = None, title: str = 'grafico', legends: list = ['linha a', 'linha b']):

    eixo_x, eixo_y = x_data, y_data
    label_a, label_b = legends[0], legends[1]
    plt.title(title)
    plt.plot(eixo_x, eixo_y, color="red", label=label_a)

    if second_data is not None:
        eixo_second_x, eixo_second_y = second_data[0], second_data[1]
        plt.plot(eixo_second_x, eixo_second_y, color="blue", label=label_b)

    plt.xticks(rotation=45)
    plt.legend();
    plt.savefig('c:/tmp/grafico_line.png') 
    plt.close()


def create_graphic_bar(x_data):
    plt.hist(x_data, 5, facecolor='blue', alpha=0.5)
    plt.title('Grafico Histograma')
    plt.xticks(rotation=45)
    plt.savefig('c:/tmp/grafico_bar.png')
    plt.close()


def create_graphic_pizza(data: dict):
    sizes = data['sizes']
    explode = data['explode']
    labels = data['labels']
    plt.pie(
        sizes, 
        explode=explode, 
        labels=labels, 
        autopct='%1.1f%%', 
        shadow=True, 
        startangle=90
    )
    plt.title('Grafico Pizza')
    plt.savefig('c:/tmp/grafico_pie.png')
    plt.close()


def format_num(num, f=False):
        a = '{:,.0f}'.format(float(num)) if not f else '{:,.2f}'.format(float(num))
        b = a.replace(',', 'v')
        c = b.replace('.', ',')
        d = c.replace('v', '.')
        return f'{d}'
