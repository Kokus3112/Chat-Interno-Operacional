import argparse
import os
import socket
import threading
import time
import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

from chat_common import close_socket, load_config, make_message, receive_packets, send_packet, today_text


class ChatClientApp:
    def __init__(self, username):
        self.config = load_config()
        self.username = username.strip().upper()
        self.client_config = self.config["clients"][self.username]
        self.server_host = self.config["server_host"]
        self.server_port = int(self.config["server_port"])
        self.reconnect_seconds = int(self.config.get("reconnect_seconds", 5))
        self.message_limit = int(self.config.get("message_limit", 8192))

        self.sock = None
        self.connected = False
        self.stop_event = threading.Event()
        self.socket_lock = threading.Lock()

        self.root = tk.Tk()
        self.root.title(self.client_config["title"])
        self.root.geometry("520x600")
        self.root.minsize(420, 420)
        self.root.protocol("WM_DELETE_WINDOW", self.minimize_to_taskbar)

        self.build_ui()
        self.load_history()
        threading.Thread(target=self.connection_loop, daemon=True).start()

    def build_ui(self):
        main = ttk.Frame(self.root, padding=10)
        main.pack(fill="both", expand=True)

        header = ttk.Frame(main)
        header.pack(fill="x", pady=(0, 8))

        self.status_label = ttk.Label(header, text="Conectando...", foreground="#a15c00")
        self.status_label.pack(side="left")

        self.connected_label = ttk.Label(header, text="Online: nenhum")
        self.connected_label.pack(side="right")

        self.chat_area = scrolledtext.ScrolledText(main, state="disabled", wrap="word")
        self.chat_area.pack(fill="both", expand=True)

        controls = ttk.Frame(main)
        controls.pack(fill="x", pady=(8, 0))

        destinations = list(self.client_config["destinations"])
        if "TODOS" not in destinations:
            destinations.append("TODOS")

        self.destination_combo = ttk.Combobox(controls, values=destinations, state="readonly", width=18)
        self.destination_combo.set(self.client_config["default_destination"])
        self.destination_combo.pack(side="left", padx=(0, 8))

        self.message_entry = ttk.Entry(controls)
        self.message_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.message_entry.bind("<Return>", lambda event: self.send_message())

        self.send_button = ttk.Button(controls, text="Enviar", command=self.send_message)
        self.send_button.pack(side="left")

    def minimize_to_taskbar(self):
        self.root.iconify()

    def history_path(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, self.client_config["history_file"])

    def append_history(self, text):
        with open(self.history_path(), "a", encoding="utf-8") as history_file:
            history_file.write(text + "\n")

    def load_history(self):
        path = self.history_path()

        if not os.path.exists(path):
            return

        self.write_chat(f"--- Histórico local de {today_text()} ---", save=False, notify=False)

        with open(path, "r", encoding="utf-8") as history_file:
            lines = history_file.readlines()[-80:]

        for line in lines:
            self.write_chat(line.rstrip("\n"), save=False, notify=False)

    def write_chat(self, text, save=True, notify=True):
        def update():
            self.chat_area.config(state="normal")
            self.chat_area.insert(tk.END, text + "\n")
            self.chat_area.config(state="disabled")
            self.chat_area.yview(tk.END)

            if notify:
                self.root.deiconify()
                self.root.lift()
                self.root.attributes("-topmost", True)
                self.root.after(900, lambda: self.root.attributes("-topmost", False))

            if save:
                self.append_history(text)

        self.root.after(0, update)

    def set_status(self, text, color):
        self.root.after(0, lambda: self.status_label.config(text=text, foreground=color))

    def set_connected_names(self, names):
        visible = ", ".join(names) if names else "nenhum"
        self.root.after(0, lambda: self.connected_label.config(text=f"Online: {visible}"))

    def connection_loop(self):
        while not self.stop_event.is_set():
            old_sock = None

            try:
                self.set_status(f"Conectando em {self.server_host}:{self.server_port}...", "#a15c00")
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(8)
                sock.connect((self.server_host, self.server_port))
                sock.settimeout(None)
                send_packet(sock, make_message("hello", name=self.username))

                with self.socket_lock:
                    self.sock = sock
                    self.connected = True

                self.set_status("Conectado", "#0b7a35")
                self.receive_loop(sock)

            except OSError:
                self.set_status(f"Desconectado. Nova tentativa em {self.reconnect_seconds}s.", "#b00020")
            finally:
                with self.socket_lock:
                    self.connected = False
                    old_sock = self.sock
                    self.sock = None

                if old_sock:
                    close_socket(old_sock)

            time.sleep(self.reconnect_seconds)

    def receive_loop(self, sock):
        for packet in receive_packets(sock, self.message_limit):
            kind = packet.get("kind")

            if kind == "chat":
                origin = packet.get("origin", "?")
                destination = packet.get("destination", "?")
                text = packet.get("text", "")
                time_text = packet.get("time", "--:--")
                self.write_chat(f"[{time_text}] {origin} -> {destination}: {text}")
            elif kind == "status":
                self.set_connected_names(packet.get("connected", []))
            elif kind == "system":
                self.write_chat(f"SISTEMA: {packet.get('text', '')}", notify=False)
            elif kind == "error":
                self.write_chat(f"SISTEMA: {packet.get('text', '')}", notify=False)

    def send_message(self):
        destination = self.destination_combo.get().strip().upper()
        text = self.message_entry.get().strip()

        if not text:
            return

        with self.socket_lock:
            sock = self.sock
            connected = self.connected

        if not connected or not sock:
            messagebox.showwarning("Chat Interno", "Sem conexão com o servidor do chat.")
            return

        try:
            send_packet(sock, make_message("chat", destination=destination, text=text))
        except OSError:
            self.write_chat("SISTEMA: não foi possível enviar. Tentando reconectar.", notify=False)
            return

        self.write_chat(f"Você -> {destination}: {text}", notify=False)
        self.message_entry.delete(0, tk.END)

    def run(self):
        self.root.mainloop()


def main():
    parser = argparse.ArgumentParser(description="Cliente do Chat Interno")
    parser.add_argument("--user", required=True, choices=["SALAO", "DELIVERY", "ESCRITORIO"])
    args = parser.parse_args()
    ChatClientApp(args.user).run()


if __name__ == "__main__":
    main()
