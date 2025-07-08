# Third-Eye
# Remote Administration Tool (RAT) Over HTTPS

This is a C&C (Command and Control) server designed for managing and interacting with multiple remote agents over secure HTTPS. It supports reverse shell access and screen sharing using a peer-to-peer UDP-based connection.

> ⚠️ **Disclaimer:** This project is intended for educational and authorized security testing purposes **only**. Unauthorized access to systems without explicit permission is illegal and unethical. The developers assume no responsibility for misuse of this tool.

---

## ✨ Features

- **Reverse HTTPS Shell**: Secure encrypted shell communication between the server (master) and agents.
- **P2P Screen Sharing**: Real-time view of the infected agent’s screen using peer-to-peer UDP.
- **Multi-Agent Management**: Interact with and control multiple agents at once.

---

## 🛠️ Actions and Controls

| Key | Action Description |
|-----|---------------------|
| `j/k` | Scroll through connected agents |
| `i` | Interact with the selected agent (start reverse shell) |
| `v` | View the selected agent's screen (P2P UDP stream) |
| `e` | Execute a command on **all connected agents** simultaneously |
| `t` | Terminate connection with the selected agent |
| `q` | Exit the C&C interface |

---

## 🔒 Architecture Overview

- **C&C Server**: Accepts reverse HTTPS connections from agents and offers a CLI interface for the master to interact.
- **Agent**: Connects to the C&C server, awaits instructions, and can:
  - Launch reverse shell
  - Stream screen via P2P connection
- **Transport**:
  - Control Commands: Encrypted HTTPS
  - Screen Sharing: UDP (peer-to-peer)

---

## 📦 Requirements

- python version 3
- C compiler (e.g., `gcc`)
- OpenSSL or equivalent for HTTPS
- Unix-like system (Linux recommended)

---

## 🚀 Usage

1. **Add you ngrok auth token**  
    ```bash
    ngrok config add-authtoken <token>

2. **Update your custom C&C server url**  
    - *server*
        - src/executor_server.py > C2URL = "your custom url"
    - *agent*
        - agents/win/malware/src/windows_agent.py > C2URL = "your custom url"
3. **run the server**
    ```bash
    ./3E
