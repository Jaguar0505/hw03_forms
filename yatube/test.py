import time


def sleep_one_sec():
    print('Перерыв 1 секунда')
    time.sleep(1)
    return 'Возвращаемое значение'
        

def sleep_two_sec():
    time.sleep(2)