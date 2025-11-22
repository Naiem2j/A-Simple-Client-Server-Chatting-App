---

# **A Simple Client–Server Chatting Application**

This project is a **Python-based multi-client chat application** using **Tkinter GUI**, **Sockets**, and **Threading**.
Multiple clients can connect to a single server and exchange messages in real time over a **local network (LAN)**.

The project is ideal for **network programming practice**, **Python socket learning**, and **college presentations**.

---

## ⭐ Features

* Multi-client chat support
* Server GUI with live status
* Client GUI with message area
* Real-time messaging
* Optional file transfer support
* No external libraries needed (only Python standard library)

---

## 🛠 Technologies Used

| Component            | Technology                          |
| -------------------- | ----------------------------------- |
| Programming Language | Python 3.8+                         |
| GUI Framework        | Tkinter                             |
| Networking           | Socket, Threading                   |
| Supported OS         | Windows (Recommended), macOS, Linux |

✔ Works without any extra installation
✔ 100% Pure Python Standard Library

---

## 📁 Project Structure

```
f:\network
│
├── server_gui_multi.py        # Server-side GUI and networking
├── client_gui_multi.py        # Client-side GUI and networking
├── tempCodeRunnerFile.py      # (Optional / Temporary)
└── uploads\
      └── file.txt             # Example uploaded file
```

---

## ⚙️ Windows Setup Guide

### 1️⃣ Check Python Installation

```powershell
python --version
```

### 2️⃣ (Optional) Create Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks it:

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## ▶️ Running the Application

### **Start the Server:**

```powershell
python server_gui_multi.py
```

### **Start Client(s):**

```powershell
python client_gui_multi.py
```

✔ Open multiple clients in separate terminals
✔ All clients connect to the same server

---

## 🌐 Configuration (HOST & PORT)

In both files:

```python
HOST = "127.0.0.1"
PORT = 5050
```

### Same PC Testing:

Keep `127.0.0.1`.

### LAN Testing:

Replace with your PC’s IP:

```python
HOST = "192.168.x.x"
```

Find IP:

```powershell
ipconfig
```

---

## 💬 Usage

* Run the server → shows "Waiting for connections"
* Run clients → each client connects automatically
* Clients can send and receive messages
* If file transfer is enabled, files appear in `uploads/`

---

## 🐞 Troubleshooting (Windows)

### Tkinter Error

Reinstall Python and ensure **Tcl/Tk** is included.

### Port Already in Use

Change port in both scripts:

```python
PORT = 6060
```

### Virtual Environment not activating

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 🔒 Security Notes

This project is for **learning, demo, and LAN use only**.
For production, add:

* SSL/TLS encryption
* Authentication system
* Input validation
* Proper logging
* Error handling

---

## 🚀 Future Enhancements

* User login/registration
* Encrypted messaging (SSL)
* Private chat rooms
* Emojis & enhanced UI
* File transfer progress bar
* Database for storing chat history

---
