import os
import json
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from yt_dlp import YoutubeDL

# Конфиг
CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".yt_audio_downloader_config.json")

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            return json.load(open(CONFIG_PATH, 'r', encoding='utf-8'))
        except:
            pass
    return {
        "port": "1080",
        "output_dir": os.path.expanduser("~")
    }

def save_config(cfg):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

def download_audio(url, use_proxy, port, output_dir):
    opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': False,
        'no_warnings': True,
    }
    if use_proxy:
        opts['proxy'] = f'socks5://127.0.0.1:{port}'
    try:
        with YoutubeDL(opts) as ydl:
            ydl.download([url])
        messagebox.showinfo("Готово", f"Аудио успешно скачано в:\n{output_dir}")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

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

    # Сохраняем настройки
    cfg['port'] = port
    cfg['output_dir'] = output_path.get()
    save_config(cfg)

    threading.Thread(
        target=download_audio,
        args=(url, use_proxy, port, cfg['output_dir']),
        daemon=True
    ).start()

def choose_folder():
    folder = filedialog.askdirectory()
    if folder:
        output_path.set(folder)
        save_config({**cfg, "output_dir": folder})

def toggle_proxy(choice):
    state = ctk.NORMAL if choice == "Shadowsocks" else ctk.DISABLED
    port_entry.configure(state=state)

# UI
cfg = load_config()
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("YouTube Audio Downloader")
app.geometry("500x400")
app.resizable(False, False)

# URL
ctk.CTkLabel(app, text="URL YouTube видео:").pack(pady=(15, 5), anchor='w', padx=20)
url_entry = ctk.CTkEntry(app, width=440)
url_entry.pack(padx=20)

# Прокси режим
ctk.CTkLabel(app, text="Режим загрузки:").pack(pady=(15, 5), anchor='w', padx=20)
proxy_switch = ctk.CTkOptionMenu(app, values=["Без прокси", "Shadowsocks"], command=toggle_proxy)
proxy_switch.pack(padx=20)
proxy_switch.set("Shadowsocks" if cfg.get("port") else "Без прокси")

# Порт
ctk.CTkLabel(app, text="Порт Clash (socks5):").pack(pady=(15, 5), anchor='w', padx=20)
port_entry = ctk.CTkEntry(app, width=100)
port_entry.insert(0, cfg.get('port', '1080'))
port_entry.pack(padx=20, anchor='w')
if proxy_switch.get() != "Shadowsocks":
    port_entry.configure(state=ctk.DISABLED)

# Папка сохранения
ctk.CTkLabel(app, text="Папка сохранения:").pack(pady=(15, 5), anchor='w', padx=20)
output_path = ctk.StringVar(value=cfg.get("output_dir", os.path.expanduser("~")))
path_frame = ctk.CTkFrame(app)
path_frame.pack(fill='x', padx=20)
ctk.CTkLabel(path_frame, textvariable=output_path, width=320, anchor="w").pack(side='left', padx=(5, 10))
ctk.CTkButton(path_frame, text="Выбрать...", command=choose_folder).pack(side='left')

# Кнопка скачать
ctk.CTkButton(app, text="Скачать аудио", command=start_download).pack(pady=25)

app.mainloop()
