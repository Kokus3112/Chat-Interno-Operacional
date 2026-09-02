import socket
import threading
import tkinter as tk
import os
from tkinter import scrolledtext, ttk
from datetime import datetime

HOST = os.getenv("CHAT_HOST", "127.0.0.1")
PORT = int(os.getenv("CHAT_PORT", "5000"))

username = "SALAO"
clientes = {}

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()


def hora():
    return datetime.now().strftime("%H:%M")


def mostrar_mensagem(msg):
    chat_area.config(state="normal")
    chat_area.insert(tk.END, msg + "\n")
    chat_area.config(state="disabled")
    chat_area.yview(tk.END)

    root.after(0, root.deiconify)
    root.after(0, root.lift)
    root.after(0, lambda: root.attributes("-topmost", True))
    root.after(1000, lambda: root.attributes("-topmost", False))

    with open("historico_salao.txt", "a", encoding="utf-8") as f:
        f.write(msg + "\n")


def atualizar_status():
    conectados = ", ".join(clientes.keys()) if clientes else "nenhum cliente"
    status_label.config(text=f"Conectados: {conectados}")


def enviar_para(destino, msg):
    if destino == "SALAO":
        mostrar_mensagem(msg)
        return

    conn = clientes.get(destino)

    if conn:
        try:
            conn.send(msg.encode())
        except:
            del clientes[destino]
            atualizar_status()
            mostrar_mensagem(f"[{hora()}] SISTEMA: {destino} desconectado.")
    else:
        mostrar_mensagem(f"[{hora()}] SISTEMA: {destino} não está conectado.")


def receber_cliente(conn, nome):
    while True:
        try:
            pacote = conn.recv(1024).decode()

            if not pacote:
                break

            destino, origem, texto = pacote.split("|", 2)
            msg = f"[{hora()}] {origem} → {destino}: {texto}"

            mostrar_mensagem(msg)
            enviar_para(destino, msg)

        except:
            break

    if nome in clientes:
        del clientes[nome]

    atualizar_status()
    mostrar_mensagem(f"[{hora()}] SISTEMA: {nome} desconectado.")


def aceitar_clientes():
    status_label.config(text="Servidor rodando...")

    while True:
        conn, addr = server.accept()

        try:
            nome = conn.recv(1024).decode().strip().upper()
            clientes[nome] = conn
            atualizar_status()
            mostrar_mensagem(f"[{hora()}] SISTEMA: {nome} conectado.")

            threading.Thread(
                target=receber_cliente,
                args=(conn, nome),
                daemon=True
            ).start()

        except:
            conn.close()


def enviar_mensagem():
    destino = destino_combo.get().strip().upper()
    texto = message_entry.get().strip()

    if texto:
        msg = f"[{hora()}] {username} → {destino}: {texto}"
        mostrar_mensagem(msg)
        enviar_para(destino, msg)
        message_entry.delete(0, tk.END)


root = tk.Tk()
root.title("Chat Interno - Salão")
root.geometry("450x550")


def minimizar_ao_fechar():
    root.iconify()


root.protocol("WM_DELETE_WINDOW", minimizar_ao_fechar)

chat_area = scrolledtext.ScrolledText(root, state="disabled")
chat_area.pack(padx=10, pady=10, fill="both", expand=True)

destino_combo = ttk.Combobox(
    root,
    values=["DELIVERY", "ESCRITORIO"],
    state="readonly"
)
destino_combo.set("DELIVERY")
destino_combo.pack(padx=10, pady=5, fill="x")

message_entry = tk.Entry(root)
message_entry.pack(padx=10, pady=5, fill="x")
message_entry.bind("<Return>", lambda event: enviar_mensagem())

send_button = tk.Button(root, text="Enviar", command=enviar_mensagem)
send_button.pack(pady=5)

status_label = tk.Label(root, text="Iniciando...")
status_label.pack()

threading.Thread(target=aceitar_clientes, daemon=True).start()

root.mainloop()
