import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

HOST = '127.0.0.1'
PORT = 5050

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client_socket.connect((HOST, PORT))
except:
    messagebox.showerror("Connection Error", "Server not running!")
    exit()

# ---------------------- CLIENT GUI ----------------------
window = tk.Tk()
window.title("🙋 Client Chat")
window.geometry("450x450")

# Frame for chat box
chat_frame = tk.Frame(window)
chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

chat_box = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD)
chat_box.pack(fill=tk.BOTH, expand=True)
chat_box.config(state=tk.DISABLED)

# Frame for entry + send button
bottom_frame = tk.Frame(window)
bottom_frame.pack(fill=tk.X, padx=10, pady=5)

msg_entry = tk.Entry(bottom_frame, font=("Arial", 12))
msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

def send_message(event=None):
    msg = msg_entry.get().strip()
    if msg:
        client_socket.send(msg.encode())
        msg_entry.delete(0, tk.END)

send_btn = tk.Button(bottom_frame, text="Send", command=send_message)
send_btn.pack(side=tk.RIGHT)

# Pressing Enter key will also send message
window.bind('<Return>', send_message)

# Receive messages in background
def receive_messages():
    while True:
        try:
            data = client_socket.recv(1024).decode()
            if not data:
                break
            chat_box.config(state=tk.NORMAL)
            chat_box.insert(tk.END, f"{data}\n")
            chat_box.config(state=tk.DISABLED)
            chat_box.yview(tk.END)
        except:
            break

threading.Thread(target=receive_messages, daemon=True).start()

window.mainloop()
client_socket.close()
