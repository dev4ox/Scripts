import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from urllib.parse import urljoin
import requests

# Создание папки для скачивания
download_folder = "downloaded_files"
os.makedirs(download_folder, exist_ok=True)

# URL сайта
base_url = "http://192.168.192.116:8080/"

# Укажите путь к ChromeDriver (скачанный с Chrome for Testing)
chrome_driver_path = "C:\\PortableApps\\chromedriver-win64\\chromedriver.exe"  # Замените на ваш путь!

# Настройки браузера
chrome_options = Options()
chrome_options.add_argument("--headless")  # Запуск без GUI
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# Запуск браузера с новым ChromeDriver
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Открываем страницу
driver.get(base_url)

# Ждем загрузки файлов
time.sleep(5)

# Получаем файлы
file_elements = driver.find_elements(By.CSS_SELECTOR, "a.file-item")

# Список ссылок
file_links = [urljoin(base_url, file.get_attribute("href")) for file in file_elements if file.get_attribute("href")]

# Закрываем браузер
driver.quit()

# Проверяем, нашлись ли файлы
if not file_links:
    print("Файлы не найдены.")
    exit()

print(f"Найдено {len(file_links)} файлов. Начинаем скачивание...")

# Скачивание файлов
for file_url in file_links:
    file_name = os.path.join(download_folder, os.path.basename(file_url))
    print(f"Скачивание {file_url} -> {file_name}")

    file_response = requests.get(file_url, stream=True)
    if file_response.status_code == 200:
        with open(file_name, "wb") as file:
            for chunk in file_response.iter_content(1024):
                file.write(chunk)
        print(f"Файл {file_name} загружен.")
    else:
        print(f"Ошибка при загрузке {file_url}")

print("Загрузка завершена!")
