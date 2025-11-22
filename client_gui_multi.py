
import socket
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import os
import mimetypes
from PIL import Image, ImageTk

HOST = '127.0.0.1'
PORT = 5050

class PremiumClientGUI:
    def __init__(self, root):
        self.root = root
        root.title("💬Chat -Client")
        root.geometry("680x720")
        root.resizable(True, True)
        
        # Set modern theme colors
        self.bg_color = "#1e1e2e"
        self.sidebar_color = "#252536"
        self.accent_color = "#7e57c2"
        self.text_color = "#e2e2e2"
        self.highlight_color = "#bb86fc"
        
        # Configure root background
        root.configure(bg=self.bg_color)
        
        # Apply modern theme
        self.setup_styles()
        
        # Create main container with gradient effect
        self.create_gradient_header()
        
        # Main content frame
        main_frame = ttk.Frame(root, style="Card.TFrame")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Connection status panel
        self.create_connection_panel(main_frame)
        
        # Chat area
        self.create_chat_area(main_frame)
        
        # Input area
        self.create_input_area(main_frame)
        
        # File transfer panel
        self.create_file_panel(main_frame)
        
        # Status bar
        self.create_status_bar()
        
        # Initialize connection variables
        self.client_socket = None
        self.receive_thread = None
        self.connected = False

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure colors for different widgets
        style.configure("Card.TFrame", background=self.bg_color)
        style.configure("Accent.TFrame", background=self.accent_color)
        style.configure("Sidebar.TFrame", background=self.sidebar_color)
        
        # Button styles
        style.configure("Accent.TButton", 
                       background=self.accent_color,
                       foreground=self.text_color,
                       focuscolor=style.configure(".")["background"])
        style.map("Accent.TButton",
                 background=[('active', self.highlight_color),
                           ('pressed', '#3700b3')])
        
        # Entry style
        style.configure("Modern.TEntry",
                       fieldbackground=self.sidebar_color,
                       foreground=self.text_color,
                       borderwidth=2,
                       focusthickness=3,
                       focuscolor=self.accent_color)
        
        # Label styles
        style.configure("Title.TLabel",
                       background=self.bg_color,
                       foreground=self.highlight_color,
                       font=("Segoe UI", 16, "bold"))
        style.configure("Subtitle.TLabel",
                       background=self.bg_color,
                       foreground=self.text_color,
                       font=("Segoe UI", 11))
        style.configure("Status.TLabel",
                       background=self.sidebar_color,
                       foreground=self.text_color,
                       font=("Segoe UI", 9))

    def create_gradient_header(self):
        # Create a simple gradient-like header
        header = tk.Frame(self.root, bg=self.accent_color, height=4)
        header.pack(fill=tk.X)
        
        # Add app title with modern font
        title_frame = ttk.Frame(self.root, style="Card.TFrame")
        title_frame.pack(fill=tk.X, padx=20, pady=(10, 5))
        
        ttk.Label(title_frame, text="💬Client Chat", style="Title.TLabel").pack(side=tk.LEFT)
        ttk.Label(title_frame, text="Messaging Experience", style="Subtitle.TLabel").pack(side=tk.LEFT, padx=(10, 0))

    def create_connection_panel(self, parent):
        conn_frame = ttk.Frame(parent, style="Card.TFrame")
        conn_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Server info
        server_info = ttk.Frame(conn_frame, style="Card.TFrame")
        server_info.pack(fill=tk.X, pady=5)
        
        ttk.Label(server_info, text="Server:", style="Subtitle.TLabel").pack(side=tk.LEFT)
        ttk.Label(server_info, text=f"{HOST}:{PORT}", style="Subtitle.TLabel", 
                 foreground=self.highlight_color).pack(side=tk.LEFT, padx=(5, 0))
        
        # Connection controls
        controls_frame = ttk.Frame(conn_frame, style="Card.TFrame")
        controls_frame.pack(fill=tk.X, pady=5)
        
        self.conn_status = tk.StringVar(value="🔴 Disconnected")
        status_label = ttk.Label(controls_frame, textvariable=self.conn_status, 
                               style="Subtitle.TLabel", foreground="#ff5252")
        status_label.pack(side=tk.LEFT)
        
        self.connect_btn = ttk.Button(controls_frame, text="Connect to Server", 
                                    style="Accent.TButton", command=self.connect_to_server)
        self.connect_btn.pack(side=tk.RIGHT)

    def create_chat_area(self, parent):
        chat_frame = ttk.Frame(parent, style="Card.TFrame")
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Chat header
        chat_header = ttk.Frame(chat_frame, style="Sidebar.TFrame")
        chat_header.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(chat_header, text="💭 Live Chat", style="Subtitle.TLabel", 
                 background=self.sidebar_color).pack(side=tk.LEFT, padx=10, pady=5)
        
        # Chat display with modern styling
        self.chat_box = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            width=70,
            height=20,
            bg=self.sidebar_color,
            fg=self.text_color,
            insertbackground=self.highlight_color,
            selectbackground=self.accent_color,
            font=("Segoe UI", 10),
            relief='flat',
            padx=15,
            pady=15
        )
        self.chat_box.pack(fill=tk.BOTH, expand=True)

    def create_input_area(self, parent):
        input_frame = ttk.Frame(parent, style="Card.TFrame")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Message entry with modern style
        self.msg_entry = ttk.Entry(
            input_frame,
            style="Modern.TEntry",
            font=("Segoe UI", 11)
        )
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.msg_entry.insert(0, "Type your message here...")
        self.msg_entry.bind('<FocusIn>', self.clear_placeholder)
        self.msg_entry.bind('<FocusOut>', self.restore_placeholder)
        
        # Send button with icon
        send_btn = ttk.Button(
            input_frame,
            text="📤 Send",
            style="Accent.TButton",
            command=self.send_message
        )
        send_btn.pack(side=tk.RIGHT)
        
        # Bind Enter key
        self.root.bind('<Return>', lambda e: self.send_message())

    def create_file_panel(self, parent):
        file_frame = ttk.Frame(parent, style="Card.TFrame")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(file_frame, text="📎 File Transfer", style="Subtitle.TLabel").pack(anchor="w", pady=(0, 8))
        
        # File controls
        file_controls = ttk.Frame(file_frame, style="Card.TFrame")
        file_controls.pack(fill=tk.X)
        
        attach_btn = ttk.Button(
            file_controls,
            text="📁 Attach File",
            style="Accent.TButton",
            command=self.attach_file
        )
        attach_btn.pack(side=tk.LEFT)
        
        ttk.Label(file_controls, text="Supports: Images, Videos, Documents", 
                 style="Subtitle.TLabel", foreground="#888").pack(side=tk.LEFT, padx=(15, 0))

    def create_status_bar(self):
        status_frame = ttk.Frame(self.root, style="Sidebar.TFrame")
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_var = tk.StringVar(value="Ready to connect...")
        status_label = ttk.Label(status_frame, textvariable=self.status_var, 
                               style="Status.TLabel")
        status_label.pack(side=tk.LEFT, padx=10, pady=5)
        
        ttk.Label(status_frame, text="Chat v2.0", style="Status.TLabel").pack(side=tk.RIGHT, padx=10, pady=5)

    def clear_placeholder(self, event):
        if self.msg_entry.get() == "Type your message here...":
            self.msg_entry.delete(0, tk.END)
            self.msg_entry.configure(foreground=self.text_color)

    def restore_placeholder(self, event):
        if not self.msg_entry.get():
            self.msg_entry.insert(0, "Type your message here...")
            self.msg_entry.configure(foreground="#888")

    def log(self, text, message_type="info"):
        colors = {
            "info": self.text_color,
            "success": "#4caf50",
            "warning": "#ff9800",
            "error": "#ff5252",
            "system": "#bb86fc"
        }
        
        color = colors.get(message_type, self.text_color)
        
        self.chat_box.config(state=tk.NORMAL)
        self.chat_box.insert(tk.END, text + "\n", message_type)
        self.chat_box.tag_configure(message_type, foreground=color)
        self.chat_box.config(state=tk.DISABLED)
        self.chat_box.yview(tk.END)

    def connect_to_server(self):
        if self.connected:
            # Disconnect logic
            try:
                self.client_socket.shutdown(socket.SHUT_RDWR)
                self.client_socket.close()
            except:
                pass
            self.connected = False
            self.conn_status.set("🔴 Disconnected")
            self.connect_btn.config(text="Connect to Server")
            self.log("🔴 Disconnected from server.", "system")
            self.status_var.set("Disconnected from server")
            return

        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((HOST, PORT))
        except Exception as e:
            messagebox.showerror("Connection Error", 
                               f"Could not connect to server:\n{e}\n\nPlease check if the server is running.")
            return

        self.connected = True
        self.conn_status.set("🟢 Connected")
        self.connect_btn.config(text="Disconnect")
        self.log("🟢 Successfully connected to server!", "success")
        self.status_var.set(f"Connected to {HOST}:{PORT}")
        
        self.receive_thread = threading.Thread(target=self.receive_messages, daemon=True)
        self.receive_thread.start()

    def send_message(self):
        if not self.connected:
            messagebox.showwarning("Not Connected", 
                                "Please connect to the server first.\n\nClick 'Connect to Server' to establish connection.")
            return
        
        text = self.msg_entry.get().strip()
        if not text or text == "Type your message here...":
            return
        
        try:
            payload = f"MSG::{text}\n"
            self.client_socket.sendall(payload.encode())
            self.log(f"You: {text}", "info")
            self.msg_entry.delete(0, tk.END)
            self.status_var.set("Message sent successfully")
        except Exception as e:
            messagebox.showerror("Send Error", 
                               f"Could not send message:\n{e}\n\nConnection may be lost.")
            self.status_var.set("Failed to send message")

    def attach_file(self):
        if not self.connected:
            messagebox.showwarning("Not Connected", 
                                "Please connect to the server first.\n\nClick 'Connect to Server' to establish connection.")
            return
        
        file_path = filedialog.askopenfilename(
            title="Select file to send",
            filetypes=[
                ("All files", "*.*"),
                ("Images", "*.jpg *.jpeg *.png *.gif *.bmp"),
                ("Videos", "*.mp4 *.avi *.mov *.mkv"),
                ("Documents", "*.pdf *.doc *.docx *.txt")
            ]
        )
        
        if not file_path:
            return
        
        filename = os.path.basename(file_path)
        filesize = os.path.getsize(file_path)
        mimetype, _ = mimetypes.guess_type(file_path)
        if mimetype is None:
            mimetype = "application/octet-stream"
        
        header = f"FILE::{filename}::{filesize}::{mimetype}\n"
        
        try:
            # Show progress
            self.status_var.set(f"Sending {filename}...")
            
            # Send header
            self.client_socket.sendall(header.encode())
            
            # Send file bytes with progress simulation
            with open(file_path, "rb") as f:
                sent = 0
                while True:
                    chunk = f.read(4096)
                    if not chunk:
                        break
                    self.client_socket.sendall(chunk)
                    sent += len(chunk)
                    # Update progress in status bar
                    progress = (sent / filesize) * 100
                    self.status_var.set(f"Sending {filename}: {progress:.1f}%")
            
            self.log(f"📤 File sent: {filename} ({self.format_size(filesize)})", "success")
            self.status_var.set(f"File {filename} sent successfully")
            
        except Exception as e:
            messagebox.showerror("File Send Error", 
                               f"Could not send file:\n{e}\n\nConnection may be lost.")
            self.status_var.set("Failed to send file")

    def format_size(self, size_bytes):
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def receive_messages(self):
        buffer = ""
        try:
            while True:
                data = self.client_socket.recv(1024)
                if not data:
                    break
                
                try:
                    text = data.decode()
                    buffer += text
                    
                    while '\n' in buffer:
                        line, buffer = buffer.split('\n', 1)
                        
                        if line.startswith("MSG::"):
                            body = line[5:]
                            self.log(body, "info")
                        elif line.startswith("NOTIFY::"):
                            self.log(line[8:], "system")
                        else:
                            self.log(line, "info")
                            
                except UnicodeDecodeError:
                    self.log("[Binary data received]", "warning")
                    
        except Exception as e:
            self.log(f"⚠️ Connection error: {e}", "error")
        finally:
            if self.client_socket:
                self.client_socket.close()
            self.connected = False
            self.conn_status.set("🔴 Disconnected")
            self.connect_btn.config(text="Connect to Server")
            self.log("🔴 Server connection closed.", "system")
            self.status_var.set("Disconnected from server")

def main():
    root = tk.Tk()
    
    # Set window icon (you can add an actual icon file)
    try:
        root.iconbitmap("chat_icon.ico")  # Add your icon file
    except:
        pass
    
    app = PremiumClientGUI(root)
    
    def on_closing():
        if app.connected:
            try:
                app.client_socket.close()
            except:
                pass
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()