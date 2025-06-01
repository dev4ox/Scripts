import os
import json
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from yt_dlp import YoutubeDL
from datetime import datetime

# --- Конфигурация ---
CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".yt_audio_downloader_config.json")

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            return json.load(open(CONFIG_PATH, 'r', encoding='utf-8'))
        except:
            pass
    return {
        "port": "1080",
        "output_dir": os.path.expanduser("~"),
        "history": []
    }

def save_config(cfg):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

# --- Загрузка и логика ---
def download_audio(url, use_proxy, port, output_dir):
    update_progress(0.1, "Начинаю загрузку...")
    opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
        'progress_hooks': [progress_hook],
    }
    if use_proxy:
        opts['proxy'] = f'socks5://127.0.0.1:{port}'
    try:
        with YoutubeDL(opts) as ydl:
            ydl.download([url])
        update_progress(1.0, "Готово: загрузка завершена.")
        log("Успешно загружено.")
    except Exception as e:
        update_progress(0, "Ошибка загрузки.")
        log(f"[Ошибка] {str(e)}", error=True)

def start_download():
    url = url_entry.get().strip()
    if not url:
        messagebox.showwarning("Внимание", "Введите URL YouTube-видео.")
        return
    use_proxy = proxy_switch.get() == "Shadowsocks"
    port = port_entry.get().strip()
    if use_proxy and not port.isdigit():
        messagebox.showwarning("Внимание", "Некорректный порт.")
        return

    cfg['port'] = port
    cfg['output_dir'] = output_path.get()
    save_config(cfg)

    log(f"▶️ Начинаем загрузку: {url}")
    threading.Thread(
        target=download_audio,
        args=(url, use_proxy, port, cfg['output_dir']),
        daemon=True
    ).start()

def progress_hook(d):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '0.0%').strip().replace('%', '')
        update_progress(float(percent) / 100.0, f"Загрузка... {percent}%")
    elif d['status'] == 'finished':
        fname = os.path.basename(d['filename'])
        cfg.setdefault("history", []).append({
            "file": fname,
            "time": datetime.now().strftime('%Y-%m-%d %H:%M')
        })
        save_config(cfg)
        update_history()

def choose_folder():
    folder = filedialog.askdirectory()
    if folder:
        output_path.set(folder)
        save_config({**cfg, "output_dir": folder})

def toggle_proxy(choice):
    state = ctk.NORMAL if choice == "Shadowsocks" else ctk.DISABLED
    port_entry.configure(state=state)

def update_progress(value, text=""):
    progress_bar.set(value)
    progress_label.configure(text=text)

def log(msg, error=False):
    color = "red" if error else "white"
    log_text.configure(state="normal")
    log_text.insert("end", f"{msg}\n", color)
    log_text.configure(state="disabled")
    log_text.yview("end")

def update_history():
    history_box.configure(values=[
        f"{item['time']} — {item['file']}"
        for item in cfg.get("history", [])[-10:][::-1]
    ])
    if cfg.get("history"):
        history_box.set(cfg["history"][-1]["file"])

# --- Новая функция вставки из буфера ---
def paste_from_clipboard():
    try:
        clip = app.clipboard_get().strip()
        url_entry.delete(0, 'end')
        url_entry.insert(0, clip)
    except Exception:
        messagebox.showwarning("Внимание", "Буфер пуст или содержит недопустимые данные.")

# --- UI ---
cfg = load_config()
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("YouTube Audio Downloader")
app.geometry("550x650")
app.resizable(False, False)

# --- Поля ---
ctk.CTkLabel(app, text="URL YouTube видео:").pack(pady=(10, 5), anchor='w', padx=20)
url_entry = ctk.CTkEntry(app, width=480)
url_entry.pack(padx=20)

# Кнопка "Вставить из буфера"
ctk.CTkButton(app, text="Вставить из буфера", command=paste_from_clipboard).pack(padx=20, pady=(5, 10), anchor='w')

ctk.CTkLabel(app, text="Режим загрузки:").pack(pady=(15, 5), anchor='w', padx=20)
proxy_switch = ctk.CTkOptionMenu(app, values=["Без прокси", "Shadowsocks"], command=toggle_proxy)
proxy_switch.pack(padx=20)
proxy_switch.set("Shadowsocks" if cfg.get("port") else "Без прокси")

ctk.CTkLabel(app, text="Порт Clash (socks5):").pack(pady=(15, 5), anchor='w', padx=20)
port_entry = ctk.CTkEntry(app, width=100)
port_entry.insert(0, cfg.get('port', '1080'))
port_entry.pack(padx=20, anchor='w')
if proxy_switch.get() != "Shadowsocks":
    port_entry.configure(state=ctk.DISABLED)

ctk.CTkLabel(app, text="Папка сохранения:").pack(pady=(15, 5), anchor='w', padx=20)
output_path = ctk.StringVar(value=cfg.get("output_dir", os.path.expanduser("~")))
path_frame = ctk.CTkFrame(app)
path_frame.pack(fill='x', padx=20)
ctk.CTkLabel(path_frame, textvariable=output_path, width=360, anchor="w").pack(side='left', padx=(5, 10))
ctk.CTkButton(path_frame, text="Выбрать...", command=choose_folder).pack(side='left')

# Кнопка скачать
ctk.CTkButton(app, text="Скачать аудио", command=start_download).pack(pady=15)

# Прогресс-бар
progress_bar = ctk.CTkProgressBar(app, width=480)
progress_bar.pack(padx=20, pady=(5, 2))
progress_bar.set(0)
progress_label = ctk.CTkLabel(app, text="")
progress_label.pack()

# Журнал логов
ctk.CTkLabel(app, text="Журнал загрузки:").pack(pady=(10, 0), anchor='w', padx=20)
log_text = ctk.CTkTextbox(app, height=100, width=480)
log_text.pack(padx=20)
log_text.tag_config("red", foreground="red")
log_text.tag_config("white", foreground="white")
log_text.configure(state="disabled")

# История
ctk.CTkLabel(app, text="Последние загрузки:").pack(pady=(15, 5), anchor='w', padx=20)
history_box = ctk.CTkComboBox(app, values=[], width=480)
history_box.pack(padx=20)
update_history()

app.mainloop()
