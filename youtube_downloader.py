import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import yt_dlp
import threading
from datetime import datetime

# ================= CONFIG =================
HISTORICO_ARQ = "historico_downloads.txt"

BG = "#0f0f0f"
CARD = "#1c1c1c"
FG = "#ffffff"
ACCENT = "#00e676"

# ================= FUNÇÕES =================
def log_historico(texto):
    with open(HISTORICO_ARQ, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().strftime('%d/%m/%Y %H:%M')} - {texto}\n")

def obter_titulo():
    try:
        with yt_dlp.YoutubeDL({
            'quiet': True,
            'cookiefile': 'cookies.txt'
        }) as ydl:
            info = ydl.extract_info(entry_url.get(), download=False)

            if info and info.get("_type") == "playlist":
                titulo_var.set(f"Playlist: {info.get('title', 'Sem título')}")
            elif info:
                titulo_var.set(info.get("title", "Não encontrado"))
            else:
                titulo_var.set("Não encontrado")
    except Exception:
        titulo_var.set("Erro ao buscar título")

def baixar():
    if not entry_url.get() or not pasta_var.get():
        messagebox.showerror("Erro", "Informe a URL e a pasta")
        return

    progresso['value'] = 0
    progresso_label.config(text="0%")

    def hook(d):
        if d['status'] == 'downloading':
            try:
                p = float(d.get('_percent_str', '0').replace('%', ''))
                progresso['value'] = p
                progresso_label.config(text=f"{int(p)}%")
            except:
                pass

    ydl_opts = {
        # 🔥 ESSENCIAL PRA 2025
        'cookiefile': 'cookies.txt',
        'noplaylist': False,
        'extract_flat': False,
        'ignoreerrors': True,
        'quiet': True,

        # anti-bloqueio
        'sleep_interval': 2,
        'max_sleep_interval': 5,

        'outtmpl': f"{pasta_var.get()}/%(playlist_index)s - %(title)s.%(ext)s",
        'progress_hooks': [hook],
    }

    if tipo_var.get() == "video":
        ydl_opts.update({
            'format': f"bestvideo[height<={qualidade_var.get()}]+bestaudio/best",
            'merge_output_format': 'mp4'
        })
    else:
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }]
        })

    def run():
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(entry_url.get(), download=True)

                if info and info.get("_type") == "playlist":
                    total = len([e for e in info.get("entries", []) if e])
                    log_historico(f"PLAYLIST baixada ({total} itens)")
                elif info:
                    log_historico(info.get("title", "Vídeo"))

            messagebox.showinfo("Sucesso", "Download finalizado!")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    threading.Thread(target=run, daemon=True).start()

def escolher_pasta():
    pasta = filedialog.askdirectory()
    if pasta:
        pasta_var.set(pasta)

# ================= UI =================
janela = tk.Tk()
janela.title("YouTube Downloader Premium")
janela.geometry("640x560")
janela.configure(bg=BG)
janela.resizable(False, False)

titulo_var = tk.StringVar(value="Título do vídeo ou playlist")
tipo_var = tk.StringVar(value="video")
qualidade_var = tk.StringVar(value="1080")
pasta_var = tk.StringVar()

style = ttk.Style()
style.theme_use("default")
style.configure("TProgressbar", thickness=12)

tk.Label(
    janela,
    text="YouTube Downloader",
    bg=BG,
    fg=ACCENT,
    font=("Segoe UI", 18, "bold")
).pack(pady=15)

card = tk.Frame(janela, bg=CARD)
card.pack(padx=20, pady=10, fill="x")

tk.Label(card, text="URL do YouTube", bg=CARD, fg=FG).pack(pady=5)
entry_url = tk.Entry(card, bg="#2a2a2a", fg=FG, insertbackground=FG)
entry_url.pack(fill="x", padx=15)

tk.Button(card, text="Buscar título", command=obter_titulo).pack(pady=5)
tk.Label(card, textvariable=titulo_var, bg=CARD, fg=ACCENT, wraplength=560).pack()

opts = tk.Frame(janela, bg=CARD)
opts.pack(padx=20, pady=10, fill="x")

tk.Radiobutton(opts, text="MP4", variable=tipo_var, value="video",
               bg=CARD, fg=FG, selectcolor=CARD).pack(side="left", padx=10)

tk.Radiobutton(opts, text="MP3", variable=tipo_var, value="audio",
               bg=CARD, fg=FG, selectcolor=CARD).pack(side="left")

ttk.Combobox(
    opts,
    textvariable=qualidade_var,
    values=["1080", "720", "480"],
    state="readonly",
    width=10
).pack(side="right", padx=10)

tk.Button(janela, text="Escolher pasta", command=escolher_pasta).pack()
tk.Label(janela, textvariable=pasta_var, bg=BG, fg=FG, wraplength=600).pack()

progresso = ttk.Progressbar(janela, length=500)
progresso.pack(pady=15)

progresso_label = tk.Label(janela, text="0%", bg=BG, fg=FG)
progresso_label.pack()

tk.Button(
    janela,
    text="INICIAR DOWNLOAD",
    bg=ACCENT,
    fg="black",
    font=("Segoe UI", 12, "bold"),
    command=baixar
).pack(pady=10)

janela.mainloop()
