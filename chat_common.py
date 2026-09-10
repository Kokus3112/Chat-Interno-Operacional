import json
import os
import socket
import sys
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)

    return BASE_DIR


def config_candidates():
    candidates = [
        os.path.join(app_dir(), "chat_config.json"),
        os.path.join(BASE_DIR, "chat_config.json"),
    ]

    bundle_dir = getattr(sys, "_MEIPASS", None)
    if bundle_dir:
        candidates.append(os.path.join(bundle_dir, "chat_config.json"))

    return candidates


def load_config():
    for config_file_path in config_candidates():
        if os.path.exists(config_file_path):
            with open(config_file_path, "r", encoding="utf-8") as config_file:
                return json.load(config_file)

    raise FileNotFoundError("chat_config.json não encontrado.")


def now_text():
    return datetime.now().strftime("%H:%M")


def today_text():
    return datetime.now().strftime("%Y-%m-%d")


def make_message(kind, **data):
    data["kind"] = kind
    return data


def send_packet(sock, packet):
    raw = json.dumps(packet, ensure_ascii=False) + "\n"
    sock.sendall(raw.encode("utf-8"))


def receive_packets(sock, limit=8192):
    buffer = ""

    while True:
        chunk = sock.recv(1024)

        if not chunk:
            return

        buffer += chunk.decode("utf-8", errors="replace")

        while "\n" in buffer:
            line, buffer = buffer.split("\n", 1)

            if not line.strip():
                continue

            if len(line) > limit:
                yield make_message("error", text="Mensagem recebida era grande demais.")
                continue

            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                yield make_message("error", text="Mensagem recebida em formato inválido.")


def close_socket(sock):
    try:
        sock.shutdown(socket.SHUT_RDWR)
    except OSError:
        pass

    try:
        sock.close()
    except OSError:
        pass
