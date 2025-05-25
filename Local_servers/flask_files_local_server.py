from flask import Flask, send_from_directory
import os

app = Flask(__name__)

# Путь к директории с файлами (измените имя пользователя!)
USER = os.getenv('USERNAME')  # Получаем имя текущего пользователя
FILES_DIR = f"C:\\Users\\{USER}\\Downloads\\old"

# Проверяем, существует ли папка
if not os.path.exists(FILES_DIR):
    os.makedirs(FILES_DIR)

@app.route('/files/<path:filename>')
def download_file(filename):
    """Отдаёт файлы из указанной директории"""
    return send_from_directory(FILES_DIR, filename, as_attachment=True)

@app.route('/')
def index():
    """Список доступных файлов"""
    files = os.listdir(FILES_DIR)
    return '<br>'.join(f'<a href="/files/{file}">{file}</a>' for file in files) or "Нет доступных файлов"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
