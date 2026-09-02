import socket
import threading
import tkinter as tk
import os
from datetime import datetime
from tkinter import scrolledtext, ttk

HOST = os.getenv("CHAT_HOST", "127.0.0.1")
PORT = int(os.getenv("CHAT_PORT", "5000"))

username = "ESCRITORIO"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
client.send(username.encode())


def mostrar_mensagem(msg):
    chat_area.config(state="normal")
    chat_area.insert(tk.END, msg + "\n")
    chat_area.config(state="disabled")
    chat_area.yview(tk.END)

    root.after(0, root.deiconify)
    root.after(0, root.lift)
    root.after(0, lambda: root.attributes("-topmost", True))
    root.after(1000, lambda: root.attributes("-topmost", False))

    with open("historico_escritorio.txt", "a", encoding="utf-8") as f:
        f.write(msg + "\n")


def receber_mensagens():
    while True:
        try:
            msg = client.recv(1024).decode()

            if msg:
                mostrar_mensagem(msg)

        except:
            mostrar_mensagem("SISTEMA: conexão encerrada.")
            break


def enviar_mensagem():
    destino = destino_combo.get().strip().upper()
    texto = message_entry.get().strip()

    if texto:
        pacote = f"{destino}|{username}|{texto}"
        client.send(pacote.encode())

        msg_local = f"[{datetime.now().strftime('%H:%M')}] {username} → {destino}: {texto}"
        mostrar_mensagem(msg_local)

        message_entry.delete(0, tk.END)

root = tk.Tk()
root.title("Chat Interno - Escritório")
root.geometry("450x550")


def minimizar_ao_fechar():
    root.iconify()


root.protocol("WM_DELETE_WINDOW", minimizar_ao_fechar)

chat_area = scrolledtext.ScrolledText(root, state="disabled")
chat_area.pack(padx=10, pady=10, fill="both", expand=True)

destino_combo = ttk.Combobox(
    root,
    values=["SALAO", "DELIVERY"],
    state="readonly"
)
destino_combo.set("SALAO")
destino_combo.pack(padx=10, pady=5, fill="x")

message_entry = tk.Entry(root)
message_entry.pack(padx=10, pady=5, fill="x")
message_entry.bind("<Return>", lambda event: enviar_mensagem())

send_button = tk.Button(root, text="Enviar", command=enviar_mensagem)
send_button.pack(pady=5)

threading.Thread(target=receber_mensagens, daemon=True).start()

root.mainloop()
