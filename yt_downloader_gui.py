import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import threading
import re
import os
import sys

# --- Determina os caminhos dos recursos ---
# PyInstaller define sys._MEIPASS com o caminho dos binários bundled.
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    BASE_PATH = sys._MEIPASS        # Bundle PyInstaller
else:
    BASE_PATH = "/opt/homebrew/bin" # Desenvolvimento local

YT_DLP_PATH = os.path.join(BASE_PATH, "yt-dlp")
FFMPEG_PATH = os.path.join(BASE_PATH, "ffmpeg")


def open_file_in_finder(path):
    """Abre o arquivo no Finder, selecionando-o."""
    subprocess.run(["open", "-R", path])

def download_video():
    url = url_entry.get()
    if not url:
        messagebox.showwarning("URL Vazia", "Por favor, insira uma URL do YouTube.")
        return

    # Desabilitar o botão para evitar cliques duplos
    download_button.config(state=tk.DISABLED)
    progress_bar.config(mode='indeterminate')
    progress_bar.start()
    status_label.config(text="Iniciando download...")

    # Executar o download em uma thread separada para não bloquear a GUI
    thread = threading.Thread(target=run_yt_dlp, args=(url,))
    thread.start()

def run_yt_dlp(url):
    try:
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")

        command = [
            YT_DLP_PATH,
            # Melhor qualidade disponível; sem restringir ext para evitar
            # o bloqueio SABR do YouTube (HTTP 403) nos streams separados.
            "-f", "bestvideo+bestaudio[ext=m4a]/bestvideo+bestaudio/best",
            # Usa o cliente Android para contornar o bloqueio SABR do YouTube.
            "--extractor-args", "youtube:player_client=android,web",
            "--ffmpeg-location", FFMPEG_PATH,
            "-o", f"{downloads_path}/%(title)s.%(ext)s",
            # Progresso em linhas separadas (em vez de \r) para poder ler linha a linha.
            "--newline",
            "--no-warnings",
            # Imprime o caminho final do arquivo após mover/mesclar.
            "--print", "after_move:filepath",
            url,
        ]

        # Mescla stderr no stdout para ler tudo em um único loop sem deadlock.
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        final_filepath = ""
        error_lines = []

        for line in process.stdout:
            line = line.strip()
            if not line:
                continue

            # Progresso: "[download]  45.2% of 32.49MiB ..."
            match = re.search(r'\[download\]\s+(\d+\.?\d*)%', line)
            if match:
                percent = float(match.group(1))
                progress_bar.stop()
                progress_bar.config(mode='determinate')
                progress_bar['value'] = percent
                status_label.config(text=f"Baixando... {percent:.1f}%")

            # Mescla de streams com ffmpeg
            elif "[Merger]" in line or "Merging" in line:
                status_label.config(text="Convertendo com ffmpeg...")
                progress_bar.config(mode='indeterminate')
                progress_bar.start()

            # Caminho final impresso por --print after_move:filepath
            elif line.startswith("/") and not line.startswith("//:"):
                final_filepath = line

            # Coleta linhas de erro para exibição em caso de falha
            elif "ERROR" in line:
                error_lines.append(line)

        process.wait()
        progress_bar.stop()
        progress_bar.config(mode='determinate')

        if process.returncode == 0:
            progress_bar['value'] = 100
            status_label.config(text="Download concluído!")
            nome = os.path.basename(final_filepath) if final_filepath else "arquivo"
            if messagebox.askyesno("Sucesso", f"Download concluído!\nArquivo: {nome}\n\nDeseja ver no Finder?"):
                open_file_in_finder(final_filepath)
        else:
            erro = "\n".join(error_lines) if error_lines else "Erro desconhecido."
            messagebox.showerror("Erro no Download", f"Ocorreu um erro:\n{erro}")
            status_label.config(text="Falha no download.")
            progress_bar['value'] = 0

    except Exception as e:
        messagebox.showerror("Erro Inesperado", str(e))
        status_label.config(text="Ocorreu um erro inesperado.")
        progress_bar['value'] = 0
    finally:
        download_button.config(state=tk.NORMAL)


# --- Configuração da Interface Gráfica ---
root = tk.Tk()
root.title("YT Downloader")
root.geometry("500x200")

frame = ttk.Frame(root, padding="20")
frame.pack(fill=tk.BOTH, expand=True)

url_label = ttk.Label(frame, text="URL do Vídeo do YouTube:")
url_label.pack(pady=5)

url_entry = ttk.Entry(frame, width=50)
url_entry.pack(fill=tk.X, expand=True, pady=5)

download_button = ttk.Button(frame, text="Baixar Vídeo", command=download_video)
download_button.pack(pady=10)

progress_bar = ttk.Progressbar(frame, orient=tk.HORIZONTAL, length=400, mode='determinate')
progress_bar.pack(pady=5)

status_label = ttk.Label(frame, text="Aguardando URL...")
status_label.pack(pady=5)

root.mainloop()
