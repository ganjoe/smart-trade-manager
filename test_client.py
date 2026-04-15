import socket
import time
import sys

msg_to_send = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Hallo"

s = socket.socket()
s.connect(("127.0.0.1", 9999))

s.sendall(b"human\n")
# read registration response
time.sleep(0.5)
s.recv(1024)

s.sendall(f"@stm {msg_to_send}\n".encode("utf-8"))

print(f"Waiting for response from STM for: '{msg_to_send}'...")
try:
    response = s.recv(4096).decode("utf-8")
    print("Response:\n", response)
except Exception as e:
    print("Socket error:", e)
s.close()
