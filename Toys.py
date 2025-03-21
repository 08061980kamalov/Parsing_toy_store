# -*- coding: utf-8 -*-
"""Untitled5.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/18-qBPn-kEonou3PsxTgqml42WalbNsAS
"""

# Импорт библиотек

import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import re

"""###Функции"""

# Функция для получения всех внутренних ссылок
def get_internal_links(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Извлекаем базовый домен
    base_domain = '/'.join(url.split('/')[:3])  # Пример: https://khabarovsk.richfamily.ru

    # Список для хранения внутренних ссылок
    internal_links = set()  # Используем set, чтобы избежать дубликатов

    # Находим все теги <a> с атрибутом href
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']

        # Пропускаем пустые ссылки и якорные ссылки (начинаются с #)
        if not href or href.startswith('#'):
            continue

        # Преобразуем относительные ссылки в абсолютные
        full_url = urljoin(base_domain, href)

        # Проверяем, что ссылка ведет на тот же домен
        if full_url.startswith(base_domain):
            internal_links.add(full_url)

    return list(internal_links)

# Функция для удаления цифр и слэшей на конце ссылки
def remove_trailing_numbers(url):
    # Используем регулярное выражение для удаления цифр и слэшей на конце
    return re.sub(r'/\d+/$', '/', url)

# Функция для получения всех ссылок на товары
def get_product_links(page_url):
    response = requests.get(page_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Список для хранения ссылок на товары
    product_links = []

    # Находим все теги <div class="card">
    for div_card in soup.find_all('div', class_='card'):
        # Ищем следующий за ним тег <a href=...>
        a_tag = div_card.find_next('a', href=True)
        if a_tag:
            href = a_tag['href']
            # Преобразуем относительные ссылки в абсолютные
            full_url = urljoin(page_url, href)
            product_links.append(full_url)

    return product_links

# Функция для извлечения данных о товаре
def get_product_data(product_url):
    response = requests.get(product_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # 1. Категория товара
    breadcrumbs = soup.find('div', class_='breadcrumbs')
    if breadcrumbs:
        category = breadcrumbs.find_all('a')[-1].text.strip()  # Последний тег <a>
    else:
        category = 'Нет категории'

    # 2. Наименование товара
    if breadcrumbs:
        name = breadcrumbs.find('span').text.strip()  # Текст внутри <span>
    else:
        name = 'Нет названия'

    # 3. Цена товара
    price = soup.find('span', class_='actual rub')
    if price:
        price = price.text.strip()
    else:
        price = 'Нет цены'

    # 4. Список ссылок на изображения товара
    images = []
    image_section = soup.find('section', class_='image')
    if image_section:
        for link_tag in image_section.find_all('link', href=True):
            images.append(link_tag['href'])

    # 5. Описание товара
    description_div = soup.find('div', id='div')
    if description_div:
        description = ' '.join(p.text.strip() for p in description_div.find_all('p'))  # Объединяем текст из всех <p>
    else:
        description = 'Нет описания'

    # Возвращаем данные в виде словаря
    return {
        'Категория': category,
        'Наименование': name,
        'Цена': price,
        'Изображения': images,
        'Описание': description
    }

"""###Основной код"""

#Создаем пустые списки для последующего заполнения базы
category_list = []
name_list = []
price_list = []
images_list = []
description_list = []

# URL страницы
url = 'https://khabarovsk.richfamily.ru/catalog/igrushki/'

# Заголовки для имитации запроса от браузера
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# Получаем все внутренние ссылки
internal_links = get_internal_links(url)

# Фильтруем ссылки, оставляя только те, которые содержат "/catalog/igrushki/"
filtered_links = [link for link in internal_links if '/catalog/igrushki/' in link]

# Сортируем ссылки (по умолчанию сортировка лексикографическая)
sorted_links = sorted(filtered_links)

# Обрабатываем ссылки
processed_links = set()  # Используем set для хранения уникальных ссылок
for link in sorted_links:
    # Удаляем цифры и слэши на конце
    cleaned_link = remove_trailing_numbers(link)
    processed_links.add(cleaned_link)
    # Преобразуем set обратно в list и сортируем
unique_links = sorted(processed_links)
#print(unique_links)
for i in range(len(unique_links)):
  unique_link = unique_links[i]
  # Получаем ссылки на товары
  product_links = get_product_links(unique_link)
  #print(product_links)
  for j in range(len(product_links)):
    # Cсылки на товар
    product_url = product_links[j]
    # Получаем данные о товаре
    product_data = get_product_data(product_url)
    #Заполнение списков
    category_list.append(product_data['Категория'])
    name_list.append(product_data['Наименование'])
    price_list.append(product_data['Цена'])
    images_list.append(product_data['Изображения'])
    description_list.append(product_data['Описание'])



# Создаем новый DataFrame из новых данных
df = {
    'Категория': category_list,
    'Наименование': name_list,
    'Цена': price_list,
    'Изображение': images_list,
    'Описание': description_list
}
data = pd.DataFrame(df)
# Сохранение в CSV
data.to_csv('toys_data.csv', index=False, encoding='utf-8')

# Сохраняем DataFrame в файл Excel
data.to_excel('toys_data.xlsx', index=False)

data.head()