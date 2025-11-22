
import socket
import threading
import os
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from PIL import Image, ImageTk
import pathlib
from datetime import datetime

HOST = '0.0.0.0'
PORT = 5050
UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)

class PremiumMultiServerGUI:
    def __init__(self, root):
        self.root = root
        root.title("🚀Chat Server - Control Panel")
        root.geometry("900x800")
        root.resizable(True, True)
        
        # Modern color scheme
        self.bg_color = "#0f172a"
        self.card_color = "#1e293b"
        self.sidebar_color = "#334155"
        self.accent_color = "#7e57c2"
        self.success_color = "#10b981"
        self.warning_color = "#f59e0b"
        self.error_color = "#ef4444"
        self.text_color = "#e2e8f0"
        
        root.configure(bg=self.bg_color)
        self.setup_styles()
        
        # Create header
        self.create_header()
        
        # Main container
        main_container = ttk.Frame(root, style="Card.TFrame")
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Server controls
        self.create_server_controls(main_container)
        
        # ✅ SERVER MESSAGE PANEL 
        self.create_server_message_panel(main_container)
        
        # Statistics panel
        self.create_stats_panel(main_container)
        
        # Chat and clients area
        self.create_chat_clients_area(main_container)
        
        # Status bar
        self.create_status_bar()
        
        # Initialize server variables
        self.server_socket = None
        self.accept_thread = None
        self.running = False
        self.clients = []
        self.lock = threading.Lock()
        self.message_count = 0
        self.file_count = 0

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure("Card.TFrame", background=self.card_color)
        style.configure("Dark.TFrame", background=self.bg_color)
        style.configure("Sidebar.TFrame", background=self.sidebar_color)
        
        # Button styles
        style.configure("Accent.TButton",
                       background=self.accent_color,
                       foreground=self.text_color,
                       font=("Segoe UI", 10, "bold"))
        style.map("Accent.TButton",
                 background=[('active', '#956ee6'),
                           ('pressed', '#65499c')])
        
        style.configure("Success.TButton",
                       background=self.success_color,
                       foreground="white")
        style.map("Success.TButton",
                 background=[('active', '#34d399'),
                           ('pressed', '#059669')])
        
        style.configure("Danger.TButton",
                       background=self.error_color,
                       foreground="white")
        style.map("Danger.TButton",
                 background=[('active', '#f87171'),
                           ('pressed', '#dc2626')])
        
        # Label styles
        style.configure("Title.TLabel",
                       background=self.bg_color,
                       foreground=self.text_color,
                       font=("Segoe UI", 18, "bold"))
        style.configure("Subtitle.TLabel",
                       background=self.card_color,
                       foreground=self.text_color,
                       font=("Segoe UI", 11))
        style.configure("Stat.TLabel",
                       background=self.sidebar_color,
                       foreground=self.text_color,
                       font=("Segoe UI", 20, "bold"))
        style.configure("StatTitle.TLabel",
                       background=self.sidebar_color,
                       foreground="#94a3b8",
                       font=("Segoe UI", 10))
        
        # Entry style
        style.configure("Modern.TEntry",
                       fieldbackground=self.sidebar_color,
                       foreground=self.text_color,
                       borderwidth=2,
                       focusthickness=3,
                       focuscolor=self.accent_color)

    def create_header(self):
        header_frame = ttk.Frame(self.root, style="Dark.TFrame")
        header_frame.pack(fill=tk.X, padx=20, pady=(15, 0))
        
        ttk.Label(header_frame, text="🚀 Chat Server", style="Title.TLabel").pack(side=tk.LEFT)
        
        # Server status indicator
        self.status_indicator = tk.Canvas(header_frame, width=20, height=20, bg=self.bg_color, highlightthickness=0)
        self.status_indicator.pack(side=tk.RIGHT, padx=(0, 10))
        self.draw_status_indicator("stopped")
        
        ttk.Label(header_frame, text="Control Panel", 
                 style="Subtitle.TLabel", foreground="#94a3b8").pack(side=tk.RIGHT, padx=(0, 20))

    def draw_status_indicator(self, status):
        self.status_indicator.delete("all")
        colors = {
            "running": self.success_color,
            "stopped": self.error_color,
            "warning": self.warning_color
        }
        color = colors.get(status, self.error_color)
        self.status_indicator.create_oval(2, 2, 18, 18, fill=color, outline="")

    def create_server_controls(self, parent):
        controls_frame = ttk.Frame(parent, style="Card.TFrame")
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Server info
        info_frame = ttk.Frame(controls_frame, style="Card.TFrame")
        info_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(info_frame, text=f"📍 Server Address: {HOST}:{PORT}", 
                 style="Subtitle.TLabel").pack(side=tk.LEFT)
        
        self.server_status = ttk.Label(info_frame, text="🛑 Stopped", 
                                     style="Subtitle.TLabel", foreground=self.error_color)
        self.server_status.pack(side=tk.RIGHT)
        
        # Control buttons
        btn_frame = ttk.Frame(controls_frame, style="Card.TFrame")
        btn_frame.pack(fill=tk.X, pady=10)
        
        self.start_btn = ttk.Button(btn_frame, text="🚀 Start Server", 
                                  style="Success.TButton", command=self.toggle_server)
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(btn_frame, text="🔄 Refresh", 
                  style="Accent.TButton", command=self.refresh_display).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(btn_frame, text="🗑️ Clear Log", 
                  style="Danger.TButton", command=self.clear_log).pack(side=tk.LEFT)

    def create_server_message_panel(self, parent):
        """✅ SERVER MESSAGE PANEL - NOW AT THE TOP! EASY TO FIND!"""
        msg_frame = ttk.Frame(parent, style="Card.TFrame")
        msg_frame.pack(fill=tk.X, pady=(0, 15))  
        
        # Highlighted header for server messages
        header_frame = ttk.Frame(msg_frame, style="Sidebar.TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 8))
        
        ttk.Label(header_frame, text="🎯 SERVER BROADCAST MESSAGE", 
                 style="Subtitle.TLabel", background=self.sidebar_color,
                 font=("Segoe UI", 12, "bold"), foreground=self.highlight_color).pack(pady=8)
        
        ttk.Label(header_frame, text="Send message to all connected clients", 
                 style="Subtitle.TLabel", background=self.sidebar_color,
                 foreground="#94a3b8").pack(pady=(0, 8))
        
        # Input area with better visibility
        input_frame = ttk.Frame(msg_frame, style="Card.TFrame")
        input_frame.pack(fill=tk.X, pady=10)
        
        self.server_msg_entry = ttk.Entry(
            input_frame,
            style="Modern.TEntry",
            font=("Segoe UI", 12),
            width=50
        )
        self.server_msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))
        self.server_msg_entry.insert(0, "Type message here and press Enter...")
        
        # Bind focus events for placeholder
        self.server_msg_entry.bind('<FocusIn>', self.clear_server_placeholder)
        self.server_msg_entry.bind('<FocusOut>', self.restore_server_placeholder)
        
        # Larger, more prominent send button
        send_btn = ttk.Button(input_frame, text="📢 BROADCAST TO ALL", 
                  style="Accent.TButton", command=self.send_from_server)
        send_btn.pack(side=tk.RIGHT)
        
        # Bind Enter key to send message
        self.server_msg_entry.bind('<Return>', lambda e: self.send_from_server())
        
        # Status label for broadcast feedback
        self.broadcast_status = ttk.Label(msg_frame, text="Ready to broadcast...", 
                                         style="Subtitle.TLabel", foreground="#94a3b8")
        self.broadcast_status.pack(anchor="w")

    def clear_server_placeholder(self, event):
        if self.server_msg_entry.get() == "Type message here and press Enter...":
            self.server_msg_entry.delete(0, tk.END)
            self.server_msg_entry.configure(foreground=self.text_color)

    def restore_server_placeholder(self, event):
        if not self.server_msg_entry.get():
            self.server_msg_entry.insert(0, "Type message here and press Enter...")
            self.server_msg_entry.configure(foreground="#888")

    def create_stats_panel(self, parent):
        stats_frame = ttk.Frame(parent, style="Sidebar.TFrame")
        stats_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Statistics cards
        stats_container = ttk.Frame(stats_frame, style="Sidebar.TFrame")
        stats_container.pack(fill=tk.X, padx=10, pady=10)
        
        # Connected clients
        client_card = ttk.Frame(stats_container, style="Sidebar.TFrame", relief='raised', borderwidth=1)
        client_card.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Label(client_card, text="Connected Clients", style="StatTitle.TLabel").pack(pady=(10, 0))
        self.client_count_var = tk.StringVar(value="0")
        ttk.Label(client_card, textvariable=self.client_count_var, style="Stat.TLabel").pack(pady=(0, 10))
        client_card.configure(padding=20)
        
        # Messages
        msg_card = ttk.Frame(stats_container, style="Sidebar.TFrame", relief='raised', borderwidth=1)
        msg_card.pack(side=tk.LEFT, padx=(0, 15))
        
        ttk.Label(msg_card, text="Messages Sent", style="StatTitle.TLabel").pack(pady=(10, 0))
        self.msg_count_var = tk.StringVar(value="0")
        ttk.Label(msg_card, textvariable=self.msg_count_var, style="Stat.TLabel").pack(pady=(0, 10))
        msg_card.configure(padding=20)
        
        # Files
        file_card = ttk.Frame(stats_container, style="Sidebar.TFrame", relief='raised', borderwidth=1)
        file_card.pack(side=tk.LEFT)
        
        ttk.Label(file_card, text="Files Shared", style="StatTitle.TLabel").pack(pady=(10, 0))
        self.file_count_var = tk.StringVar(value="0")
        ttk.Label(file_card, textvariable=self.file_count_var, style="Stat.TLabel").pack(pady=(0, 10))
        file_card.configure(padding=20)

    def create_chat_clients_area(self, parent):
        chat_clients_frame = ttk.Frame(parent, style="Card.TFrame")
        chat_clients_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Configure grid
        chat_clients_frame.columnconfigure(0, weight=3)
        chat_clients_frame.columnconfigure(1, weight=1)
        chat_clients_frame.rowconfigure(0, weight=1)
        
        # Chat area
        chat_frame = ttk.Frame(chat_clients_frame, style="Card.TFrame")
        chat_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        ttk.Label(chat_frame, text="💬 Server Log & Chat Monitor", 
                 style="Subtitle.TLabel").pack(anchor="w", pady=(0, 5))
        
        self.chat_box = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            width=60,
            height=20,
            bg=self.sidebar_color,
            fg=self.text_color,
            insertbackground=self.accent_color,
            selectbackground=self.accent_color,
            font=("Consolas", 9),
            relief='flat',
            padx=15,
            pady=15
        )
        self.chat_box.pack(fill=tk.BOTH, expand=True)
        
        # Clients panel
        clients_frame = ttk.Frame(chat_clients_frame, style="Card.TFrame")
        clients_frame.grid(row=0, column=1, sticky="nsew")
        
        ttk.Label(clients_frame, text="👥 Connected Clients", 
                 style="Subtitle.TLabel").pack(anchor="w", pady=(0, 5))
        
        # Clients listbox with scrollbar
        listbox_frame = ttk.Frame(clients_frame, style="Card.TFrame")
        listbox_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.clients_listbox = tk.Listbox(
            listbox_frame,
            bg=self.sidebar_color,
            fg=self.text_color,
            selectbackground=self.accent_color,
            font=("Segoe UI", 10),
            relief='flat'
        )
        
        scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=self.clients_listbox.yview)
        self.clients_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.clients_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Client controls
        client_controls = ttk.Frame(clients_frame, style="Card.TFrame")
        client_controls.pack(fill=tk.X)
        
        ttk.Button(client_controls, text="🔌 Disconnect Selected", 
                  style="Danger.TButton", command=self.disconnect_selected).pack(fill=tk.X)
        
        ttk.Button(client_controls, text="📊 Client Info", 
                  style="Accent.TButton", command=self.show_client_info).pack(fill=tk.X, pady=(5, 0))

    def create_status_bar(self):
        status_frame = ttk.Frame(self.root, style="Sidebar.TFrame")
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_var = tk.StringVar(value="Server ready - Click 'Start Server' to begin")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, 
                               style="Subtitle.TLabel", background=self.sidebar_color)
        status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        ttk.Label(status_frame, text="💎 EliteChat Server v2.0", 
                 style="Subtitle.TLabel", background=self.sidebar_color,
                 foreground="#94a3b8").pack(side=tk.RIGHT, padx=10, pady=5)

    def log(self, text, level="info"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        levels = {
            "info": ("ℹ️", self.text_color),
            "success": ("✅", self.success_color),
            "warning": ("⚠️", self.warning_color),
            "error": ("❌", self.error_color),
            "system": ("🔧", self.accent_color),
            "broadcast": ("📢", "#f59e0b")  # Special color for broadcast messages
        }
        
        emoji, color = levels.get(level, ("ℹ️", self.text_color))
        formatted_text = f"[{timestamp}] {emoji} {text}"
        
        self.chat_box.config(state=tk.NORMAL)
        self.chat_box.insert(tk.END, formatted_text + "\n", level)
        self.chat_box.tag_configure(level, foreground=color)
        self.chat_box.config(state=tk.DISABLED)
        self.chat_box.yview(tk.END)
        
        if level == "info":
            self.message_count += 1
            self.msg_count_var.set(str(self.message_count))

    def toggle_server(self):
        if not self.running:
            # Start server
            try:
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.server_socket.bind((HOST, PORT))
                self.server_socket.listen(5)
            except Exception as e:
                messagebox.showerror("Server Error", 
                                   f"Could not start server:\n\n{e}\n\nCheck if port {PORT} is available.")
                return
            
            self.running = True
            self.server_status.config(text="🟢 Running", foreground=self.success_color)
            self.start_btn.config(text="🛑 Stop Server", style="Danger.TButton")
            self.draw_status_indicator("running")
            self.log(f"Server started successfully on {HOST}:{PORT}", "success")
            self.status_var.set(f"Server running on {HOST}:{PORT} - Accepting connections")
            self.broadcast_status.config(text="✅ Server ready - You can broadcast messages now!")
            
            self.accept_thread = threading.Thread(target=self.accept_connections, daemon=True)
            self.accept_thread.start()
        else:
            # Stop server
            self.running = False
            self.server_status.config(text="🛑 Stopped", foreground=self.error_color)
            self.start_btn.config(text="🚀 Start Server", style="Success.TButton")
            self.draw_status_indicator("stopped")
            self.log("Server shutdown initiated...", "warning")
            self.status_var.set("Server stopping...")
            self.broadcast_status.config(text="❌ Server stopped - Start server to broadcast")
            
            try:
                if self.server_socket:
                    self.server_socket.close()
            except:
                pass
            
            with self.lock:
                for conn, addr in list(self.clients):
                    try:
                        conn.shutdown(socket.SHUT_RDWR)
                        conn.close()
                    except:
                        pass
                self.clients.clear()
            
            self.refresh_clients_list()
            self.log("Server stopped successfully", "system")
            self.status_var.set("Server stopped - Ready to start")

    def accept_connections(self):
        while self.running:
            try:
                conn, addr = self.server_socket.accept()
            except Exception:
                break  # socket closed or error -> exit
            with self.lock:
                self.clients.append((conn, addr))
            self.log(f"✅ {addr} connected.", "success")
            self.refresh_clients_list()
            # notify other clients
            self.broadcast(f"NOTIFY::Server: {addr} joined the chat.")
            t = threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True)
            t.start()

    def refresh_clients_list(self):
        self.clients_listbox.delete(0, tk.END)
        with self.lock:
            for _, addr in self.clients:
                self.clients_listbox.insert(tk.END, f"{addr[0]}:{addr[1]}")
            self.client_count_var.set(str(len(self.clients)))
            # Update broadcast status
            if self.running:
                client_count = len(self.clients)
                if client_count > 0:
                    self.broadcast_status.config(
                        text=f"✅ Ready - {client_count} client(s) connected", 
                        foreground=self.success_color
                    )
                else:
                    self.broadcast_status.config(
                        text="⚠️ No clients connected - Wait for clients to join",
                        foreground=self.warning_color
                    )

    def broadcast(self, message, exclude_conn=None):
        # message is a text string already formatted to send as utf-8
        with self.lock:
            for conn, _ in list(self.clients):
                if conn == exclude_conn:
                    continue
                try:
                    conn.sendall(message.encode())
                except:
                    # remove dead client
                    try:
                        conn.close()
                    except:
                        pass
                    self.clients = [(c,a) for (c,a) in self.clients if c!=conn]
        self.refresh_clients_list()

    def handle_client(self, conn, addr):
        try:
            while True:
                header = conn.recv(6)  # try small peek; but we need to recv properly
                if not header:
                    break
                # Since we can't be sure how much header we have, we'll read until newline marker.
                # But our client protocol will send headers as ASCII lines terminated by '\n'
                # So if first recv didn't include full header, read until newline.
                data = header
                while b'\n' not in data:
                    more = conn.recv(1024)
                    if not more:
                        break
                    data += more
                if not data:
                    break
                header_line, _, remainder = data.partition(b'\n')
                header_str = header_line.decode()
                # Two protocol cases:
                # 1) "MSG::<text>"
                # 2) "FILE::<filename>::<filesize>::<mimetype>"
                if header_str.startswith("MSG::"):
                    text = header_str[5:]
                    self.log(f"{addr}: {text}", "info")
                    # broadcast full message
                    self.broadcast(f"MSG::{addr}: {text}", exclude_conn=conn)
                    # If remainder has extra content, ignore (shouldn't)
                elif header_str.startswith("FILE::"):
                    # parse
                    # FILE::<filename>::<filesize>::<mimetype>
                    parts = header_str.split("::", 3)
                    if len(parts) < 4:
                        self.log(f"⚠️ Bad file header from {addr}: {header_str}", "error")
                        continue
                    _, filename, filesize_str, mimetype = parts
                    try:
                        filesize = int(filesize_str)
                    except:
                        self.log(f"⚠️ Invalid filesize from {addr}: {filesize_str}", "error")
                        continue
                    safe_name = pathlib.Path(filename).name
                    save_path = os.path.join(UPLOAD_DIR, safe_name)
                    # If remainder contains some bytes of file, write them
                    received = len(remainder)
                    with open(save_path, "wb") as f:
                        if remainder:
                            f.write(remainder)
                        # continue receiving remaining bytes
                        while received < filesize:
                            chunk = conn.recv(min(4096, filesize - received))
                            if not chunk:
                                break
                            f.write(chunk)
                            received += len(chunk)
                    self.log(f"📁 Received file from {addr}: {safe_name} ({filesize} bytes) -> {save_path}", "success")
                    self.file_count += 1
                    self.file_count_var.set(str(self.file_count))
                    # announce to other clients (they can download via separate mechanism; here we just notify)
                    self.broadcast(f"NOTIFY::Server: {addr} sent file {safe_name}")
                    # If image, show preview in a window
                    if mimetype.startswith("image"):
                        try:
                            self.show_image_preview(save_path, title=f"Image from {addr}")
                        except Exception as e:
                            self.log(f"⚠️ Could not preview image: {e}", "warning")
                else:
                    # Unknown header: treat as text
                    try:
                        txt = header_str
                        self.log(f"{addr}: {txt}", "info")
                        self.broadcast(f"MSG::{addr}: {txt}", exclude_conn=conn)
                    except:
                        pass
        except Exception as e:
            self.log(f"⚠️ Connection error with {addr}: {e}", "error")
        finally:
            with self.lock:
                self.clients = [(c,a) for (c,a) in self.clients if c!=conn]
            try:
                conn.close()
            except:
                pass
            self.log(f"❌ {addr} disconnected.", "warning")
            self.refresh_clients_list()
            self.broadcast(f"NOTIFY::Server: {addr} left the chat.")

    def disconnect_selected(self):
        sel = self.clients_listbox.curselection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a client to disconnect.")
            return
        idx = sel[0]
        with self.lock:
            if idx < len(self.clients):
                conn, addr = self.clients[idx]
                try:
                    conn.shutdown(socket.SHUT_RDWR)
                except:
                    pass
                try:
                    conn.close()
                except:
                    pass
                self.clients.pop(idx)
        self.refresh_clients_list()
        self.log(f"🔌 Disconnected {addr}", "system")

    def send_from_server(self):
        """✅ SERVER MESSAGE KORAR OPTION - NOW EASY TO FIND!"""
        if not self.running:
            messagebox.showwarning("Server Not Running", 
                                "Server is not running. Please start the server first.")
            return
            
        msg = self.server_msg_entry.get().strip()
        if not msg or msg == "Type message here and press Enter...":
            messagebox.showwarning("Empty Message", "Please enter a message to broadcast.")
            return
        
        # Check if there are any clients connected
        with self.lock:
            if not self.clients:
                messagebox.showinfo("No Clients", "No clients are connected to receive the message.")
                return
        
        # Send the broadcast message
        try:
            self.broadcast(f"MSG::🚀 Server: {msg}")
            self.log(f"📢 Server Broadcast: {msg}", "broadcast")
            self.status_var.set(f"Broadcast sent to {len(self.clients)} client(s)")
            self.broadcast_status.config(
                text=f"✅ Last broadcast: '{msg}' to {len(self.clients)} client(s)", 
                foreground=self.success_color
            )
            
            # Clear the entry field
            self.server_msg_entry.delete(0, tk.END)
            
        except Exception as e:
            messagebox.showerror("Broadcast Error", 
                               f"Failed to send broadcast:\n\n{e}")
            self.log(f"❌ Broadcast failed: {e}", "error")
            self.broadcast_status.config(
                text=f"❌ Broadcast failed: {e}",
                foreground=self.error_color
            )

    def show_image_preview(self, path, title="Image"):
        try:
            top = tk.Toplevel(self.root)
            top.title(title)
            top.configure(bg=self.bg_color)
            
            img = Image.open(path)
            img.thumbnail((600, 400))
            tkimg = ImageTk.PhotoImage(img)
            
            lbl = ttk.Label(top, image=tkimg, background=self.bg_color)
            lbl.image = tkimg
            lbl.pack(padx=10, pady=10)
            
            # Add close button
            close_btn = ttk.Button(top, text="Close", command=top.destroy, style="Accent.TButton")
            close_btn.pack(pady=(0, 10))
            
        except Exception as e:
            self.log(f"⚠️ Image preview error: {e}", "error")

    def refresh_display(self):
        self.refresh_clients_list()
        self.log("Display refreshed", "system")

    def clear_log(self):
        self.chat_box.config(state=tk.NORMAL)
        self.chat_box.delete(1.0, tk.END)
        self.chat_box.config(state=tk.DISABLED)
        self.log("Log cleared", "system")

    def show_client_info(self):
        sel = self.clients_listbox.curselection()
        if not sel:
            messagebox.showinfo("Client Info", "Please select a client from the list.")
            return
        
        idx = sel[0]
        with self.lock:
            if idx < len(self.clients):
                conn, addr = self.clients[idx]
                messagebox.showinfo("Client Information", 
                                  f"📡 Client Address: {addr[0]}:{addr[1]}\n"
                                  f"🔗 Connection Status: {'Active' if conn else 'Closed'}\n"
                                  f"👥 Total Connected Clients: {len(self.clients)}\n"
                                  f"📊 Messages Processed: {self.message_count}\n"
                                  f"📁 Files Shared: {self.file_count}")

    @property
    def highlight_color(self):
        return "#ffd700"  # Gold color for highlights

def main():
    root = tk.Tk()
    
    try:
        root.iconbitmap("server_icon.ico")  # Add your server icon
    except:
        pass
    
    app = PremiumMultiServerGUI(root)
    
    def on_closing():
        if app.running:
            app.toggle_server()  # Stop server if running
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()