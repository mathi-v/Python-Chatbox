import socket
import threading
import datetime

HOST = '127.0.0.1'
PORT = 1234
LISTENER_LIMIT = 5

active_clients = []
active_clients_lock = threading.Lock()

active_usernames = set()
admin_password = "adminpass"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(LISTENER_LIMIT)

log_file_path = "server_log.txt"

def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log_message(message):
    timestamped_message = f"[{get_timestamp()}] {message}\n"
    with open(log_file_path, "a") as log_file:
        log_file.write(timestamped_message)

def print_with_timestamp(message):
    timestamped_message = f"[{get_timestamp()}] {message}"
    print(timestamped_message)
    log_message(timestamped_message)

def is_username_taken(username):
    with active_clients_lock:
        return username in active_usernames

def send_messages_to_all(message, sender_username):
    with active_clients_lock:
        for username, client_socket, address in active_clients:
            if username != sender_username:
                try:
                    client_socket.sendall(message.encode())
                except Exception as e:
                    print_with_timestamp(f"Error sending message to {username}: {e}")

# ... (existing code)

def kick_user(username):
    with active_clients_lock:
        for stored_username, client_socket, address in active_clients:
            if stored_username == username:
                try:
                    client_socket.sendall("[SERVER] You have been kicked from the chat.".encode())
                    client_socket.close()
                except Exception as e:
                    print_with_timestamp(f"Error kicking {username}: {e}")
                finally:
                    active_clients.remove((stored_username, client_socket, address))
                    active_usernames.remove(username)
                    send_messages_to_all(f"[SERVER] {username} has been kicked from the chat", username)
                    log_message(f"Client {username} has been kicked.")
                break

# ... (existing code)

def admin_commands(username, command):
    if username == "SERVER":
        parts = command.split(' ')
        if parts[0] == "?kick" and len(parts) == 2:
            kick_user(parts[1])
        # Add more admin commands as needed

# ... (existing code)

def client_handler(client_socket):
    username = None
    client_address = None
    
    try:
        username = client_socket.recv(2048).decode('utf-8')
        if not username:
            return

        if is_username_taken(username):
            client_socket.sendall("[SERVER] DUPLICATE_USERNAME".encode())
            return

        client_address = client_socket.getpeername()
        with active_clients_lock:
            active_clients.append((username, client_socket, client_address))
            active_usernames.add(username)

        print_with_timestamp(f"Client {username} connected from {client_address[0]}:{client_address[1]}")

        if username == "SERVER":
            admin_password_attempt = client_socket.recv(2048).decode('utf-8')
            if admin_password_attempt != admin_password:
                print_with_timestamp(f"Admin authentication failed for {username}. Disconnecting.")
                client_socket.sendall("[SERVER] Admin authentication failed. Disconnecting.".encode())
                return

        send_messages_to_all(f"[SERVER] {username} joined the chat", username)

        while True:
            message = client_socket.recv(2048).decode('utf-8')
            if not message:
                break

            if username == "admin" and message.startswith("=?"):
                admin_commands(username, message[2:])
            else:
                send_messages_to_all(f"{username}~~ {message}", username)
                log_message(f"{username}: {message}")

    except Exception as e:
        print_with_timestamp(f"Error in client_handler: {e}")

    finally:
        if username and client_address:
            with active_clients_lock:
                active_clients.remove((username, client_socket, client_address))
                active_usernames.remove(username)

            print_with_timestamp(f"Client {username} disconnected from {client_address[0]}:{client_address[1]}")
            send_messages_to_all(f"[SERVER] {username} left the chat", username)
            log_message(f"Client {username} disconnected.")

            client_socket.close()

def main():
    try:
        print_with_timestamp(f"Server is running on {HOST}:{PORT}")

        while True:
            client_socket, client_address = server.accept()
            threading.Thread(target=client_handler, args=(client_socket,)).start()

    except Exception as e:
        print_with_timestamp(f"Error in main: {e}")

    finally:
        server.close()

if __name__ == '__main__':
    main()



