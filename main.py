import time
import os, sys
import requests
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
import configparser

config = configparser.ConfigParser()
config.read("settings.ini")

# Данные для поиска
postUrl = config["url"]["url_post"]
url = config["url"]["url_float"]

# Технические данные
wait = config["settings"]["wait_time"]
wait_error = config["settings"]["wait_error"]
bot = config["settings"]["bot"]
cookie = config["settings"]["cookie_session"]

# Списки предметов
items = config["items"]["items"]
items_knife = config["items"]["items_knife"]
items_gloves = config["items"]["items_glove"]

name_list = items.split(',')  # Перебор предметов в массив

browser = None

'''
Функция для отправки данных POST
'''


def POST(post):
    print(requests.post(postUrl, data=post).text)


'''
Функция для запуска браузера, в зависимости 
от того в консоли или через .exe
'''


def startBrowser():
    global browser
    if getattr(sys, 'frozen', False):
        chromedriver_path = os.path.join(sys._MEIPASS, "chromedriver.exe")
        browser = webdriver.Chrome(chromedriver_path)
    else:
        browser = webdriver.Chrome()


'''
Функция для перехода на опр. стр. сайта
Добавленно ожидание, чтобы не получить баз
за частые запросы на сайт
'''


def startSearchName(search):
    global browser
    print(search)
    browser.get("https://csgofloat.com")
    browser.add_cookie({"name": "session", "value": cookie})
    browser.get(url)
    input_val = browser.find_element_by_id('mat-input-1')
    input_val.send_keys(search)
    time.sleep(1)
    browser.find_element_by_class_name('mat-option-text').click()
    time.sleep(12)
    browser.find_element_by_css_selector('.mat-raised-button').click()
    time.sleep(12)
    parser(search)


'''
Запуск цикла для прохода по массиву предметов
'''


def startSearchPage():
    for search in name_list:
        startSearchName(search)

    time.sleep(5)
    startSearchPage()


'''
Функция для проверки имени
'''


def checkName(item_name):
    item_name = item_name.replace('★', '').replace('StatTrak™', '').replace('(FN)', '').replace('(MW)', '').replace(
        '(FT)', '').replace('(BS)', '').replace('(WW)', '').strip()
    if item_name in name_list:
        return True
    else:
        return False


'''
Функция для поиска ошибки на стр.
'''


def reportText():
    global browser
    error = browser.find_elements_by_css_selector('.results > div > .ng-star-inserted > span')
    report = error[0].text
    del error
    return report


'''
Функция для разбора стр на элементы
'''


def parser(search):
    global browser

    id_item = browser.find_elements_by_class_name('cdk-column-id')
    name = browser.find_elements_by_class_name('cdk-column-name')
    history = browser.find_elements_by_css_selector('.cdk-column-history')
    inspect = browser.find_elements_by_css_selector('.cdk-column-link > div')
    i = 1

    id_len = len(id_item)

    if id_len < 10:
        sendReport(search)
        return

    while i < 20:
        name_text = name[i].text
        href = inspect[i - 1].find_element_by_tag_name('a').get_attribute('href')

        try:
            hist = history[i].find_element_by_tag_name('a').text
        except Exception:
            hist = 'No'

        if hist != 'No':
            i = i + 1
            continue

        if checkName(name_text):
            POST({
                'name': name_text,
                'id': id_item[i].text,
                'href': href,
                'hist': hist
            })

        i += 1

    os.system("cls")
    time.sleep(int(wait))


'''
Отправка сообщения об ошибке
'''


def sendReport(search):
    global browser
    POST({
        'method': 'error_parser',
        'bot': bot,
        'report': reportText()
    })
    browser.close()
    startBrowser()
    time.sleep(int(wait_error))
    startSearchName(search)  # Перезапуск цикла с тогоже места


startBrowser()

startSearchPage()
