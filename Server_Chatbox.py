import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

HOST = '127.0.0.1'
PORT = 1234

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

message_queue = []  # Queue to handle GUI updates in a thread-safe way


def connect():
    try:
        client.connect((HOST, PORT))
        print("Successfully connected to the server")
        username_button.config(text="Connected", state=tk.DISABLED)
        red_x_button.pack(side=tk.LEFT, padx=15)  # Pack the red X button after the "Connected" button
    except Exception as e:
        messagebox.showerror("Unable to connect to the server", f"No internet connection or the server is down. Try contacting \n99220041800@klu.ac.in")
        return

    username = username_textbox.get()
    if ' ' in username:
        messagebox.showerror("Invalid username", "Username cannot contain spaces.")
        client.close()
        root.destroy()
        return

    if username != '':
        client.sendall(username.encode())
        threading.Thread(target=listen_for_messages_from_server).start()
        username_textbox.config(state=tk.DISABLED)
    else:
        messagebox.showerror("Invalid username", "Username cannot be empty")

def disconnect():
    client.close()
    root.destroy()


def send_message(event=None):
    message = message_textbox.get()
    if message != '':
        add_message(f"[{username_textbox.get()}]~~ {message}")
        client.sendall(message.encode())
        message_textbox.delete(0, tk.END)
    else:
        messagebox.showerror("Empty message", "Message cannot be empty")

def listen_for_messages_from_server():
    while True:
        try:
            message = client.recv(2048).decode('utf-8')
            if not message:
                break
            if message.startswith("[SERVER] DUPLICATE_USERNAME"):
                messagebox.showerror("Duplicate Username", "Username is already taken. Please choose another one.")
                client.close()  # Close the connection immediately
                root.destroy()  # Close the client GUI
            elif message.startswith("[SERVER] You have been kicked"):
                message_queue.append(display_kick_message)
            elif message.startswith("SERVER~~ ?kick"):
                parts = message.split(' ', 2)
                if len(parts) == 3 and parts[2] == username_textbox.get():
                    message_queue.append(display_kick_message)
                else:
                    message_queue.append(lambda msg=message: add_message(msg))
            elif message.startswith("SERVER~~ ?warn"):
                parts = message.split(' ', 2)
                if len(parts) == 3:
                    message_queue.append(lambda msg=parts[2]: display_warn_message(msg))
                else:
                    message_queue.append(lambda msg=message: add_message(msg))

                    ##thebelow not working
            elif message.startswith("SERVER~~ ?kickall"):
                parts = message.split(' ', 2)
                if len(parts) == 3:
                    message_queue.append(lambda msg=parts[2]: display_warn_message(msg))
                else:
                    message_queue.append(lambda msg=message: add_message(msg))
            else:
                message_queue.append(lambda msg=message: add_message(msg))
        except Exception as e:
            print(f"Error in listen_for_messages_from_server: {e}")
            break


def add_message(message):
    if not message.startswith("SERVER~~ ?kick"):
        message_box.config(state=tk.NORMAL)
        message_box.insert(tk.END, message + '\n')
        message_box.config(state=tk.DISABLED)


def display_kick_message():
    messagebox.showinfo("Kicked", "You have been kicked from the chat.")
    client.close()
    root.destroy()  # Close the client GUI after being kicked


def display_warn_message(message):
    messagebox.showinfo("Server Warning", f"Warning from SERVER: {message}")


root = tk.Tk()
root.title("Chat Application")
root.resizable(False, False)


top_frame = tk.Frame(root, width=600, height=100, bg='#121212')
top_frame.pack(fill=tk.X)

middle_frame = tk.Frame(root, width=600, height=400, bg='#1F1B24')
middle_frame.pack(fill=tk.X)

bottom_frame = tk.Frame(root, width=600, height=100, bg='#121212')
bottom_frame.pack(fill=tk.X)

username_label = tk.Label(top_frame, text="Username:", font=("Helvetica", 17), bg='#121212', fg='white')
username_label.pack(side=tk.LEFT, padx=10)

username_textbox = tk.Entry(top_frame, font=("Helvetica", 17), bg='#1F1B24', fg='white', width=23)
username_textbox.pack(side=tk.LEFT)

username_button = tk.Button(top_frame, text="Connect", font=("Helvetica", 15), bg='#464EB8', fg='white', command=connect)
username_button.pack(side=tk.LEFT, padx=15)

# Add the following code to create the red X button
red_x_button = tk.Button(top_frame, text="X", font=("Helvetica", 15), bg='red', fg='white', command=disconnect)
# By default, keep it hidden; it will be shown after the connection is established
red_x_button.pack_forget()

message_box = scrolledtext.ScrolledText(middle_frame, font=("Helvetica", 13), bg='#1F1B24', fg='white', width=67, height=26.5)
message_box.config(state=tk.DISABLED)
message_box.pack(side=tk.TOP)

message_textbox = tk.Entry(bottom_frame, font=("Helvetica", 17), bg='#1F1B24', fg='white', width=38)
message_textbox.pack(side=tk.LEFT, padx=10)

message_button = tk.Button(bottom_frame, text="Send", font=("Helvetica", 15), bg='#464EB8', fg='white', command=send_message)
message_button.pack(side=tk.LEFT, padx=10)

root.grid_rowconfigure(0, weight=0)
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=4)
root.grid_rowconfigure(3, weight=1)

root.grid_columnconfigure(0, weight=1)

root.bind('<Return>', send_message)

def check_message_queue():
    while True:
        if message_queue:
            message_queue.pop(0)()  # Execute the function in the queue
        root.update()

# Start a thread to check the message queue
threading.Thread(target=check_message_queue, daemon=True).start()

try:
    root.mainloop()
except KeyboardInterrupt:
    print("Client shutting down...")
    client.close()



