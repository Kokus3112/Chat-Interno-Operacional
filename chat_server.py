import socket
import threading

from chat_common import close_socket, load_config, make_message, now_text, receive_packets, send_packet


config = load_config()
HOST = config["server_host"]
PORT = int(config["server_port"])
MESSAGE_LIMIT = int(config.get("message_limit", 8192))

clients = {}
clients_lock = threading.Lock()


def log(text):
    print(f"[{now_text()}] {text}", flush=True)


def connected_names():
    with clients_lock:
        return sorted(clients.keys())


def broadcast_status():
    packet = make_message("status", connected=connected_names())

    with clients_lock:
        sockets = list(clients.values())

    for client_socket in sockets:
        try:
            send_packet(client_socket, packet)
        except OSError:
            pass


def remove_client(name, client_socket):
    removed = False

    with clients_lock:
        if clients.get(name) is client_socket:
            del clients[name]
            removed = True

    if removed:
        log(f"{name} desconectado.")
        broadcast_status()


def send_to_client(destination, packet):
    with clients_lock:
        destination_socket = clients.get(destination)

    if not destination_socket:
        return False

    try:
        send_packet(destination_socket, packet)
        return True
    except OSError:
        remove_client(destination, destination_socket)
        return False


def handle_message(origin, packet):
    destination = str(packet.get("destination", "")).strip().upper()
    text = str(packet.get("text", "")).strip()

    if not destination or not text:
        return

    delivered_packet = make_message(
        "chat",
        origin=origin,
        destination=destination,
        text=text,
        time=now_text(),
    )

    if destination == "TODOS":
        for name in connected_names():
            if name != origin:
                send_to_client(name, delivered_packet)
        log(f"{origin} -> TODOS: {text}")
        return

    if send_to_client(destination, delivered_packet):
        log(f"{origin} -> {destination}: {text}")
    else:
        send_to_client(origin, make_message("error", text=f"{destination} não está conectado."))
        log(f"{origin} tentou falar com {destination}, mas o destino está offline.")


def handle_client(client_socket, address):
    name = None

    try:
        first_packet = next(receive_packets(client_socket, MESSAGE_LIMIT))
        name = str(first_packet.get("name", "")).strip().upper()

        if first_packet.get("kind") != "hello" or not name:
            close_socket(client_socket)
            return

        with clients_lock:
            old_socket = clients.get(name)
            clients[name] = client_socket

        if old_socket:
            close_socket(old_socket)

        log(f"{name} conectado de {address[0]}.")
        send_packet(client_socket, make_message("system", text="Conectado ao servidor do chat."))
        broadcast_status()

        for packet in receive_packets(client_socket, MESSAGE_LIMIT):
            if packet.get("kind") == "chat":
                handle_message(name, packet)

    except (ConnectionError, OSError, StopIteration):
        pass
    finally:
        if name:
            remove_client(name, client_socket)
        close_socket(client_socket)


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()

    log(f"Servidor do chat rodando em {HOST}:{PORT}.")

    while True:
        client_socket, address = server.accept()
        threading.Thread(target=handle_client, args=(client_socket, address), daemon=True).start()


if __name__ == "__main__":
    main()
