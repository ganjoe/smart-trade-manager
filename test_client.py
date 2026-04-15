import socket
import time

s = socket.socket()
s.connect(("127.0.0.1", 9999))

print("Registering as human...")
s.sendall(b"human\n")
print(s.recv(1024).decode())
time.sleep(1)

print("Sending message to STM...")
s.sendall(b"@stm Hallo STM, kannst du mich hoeren?\n")

print("Waiting for response from STM...")
response = s.recv(4096).decode()
print("Response:", response)
s.close()
