1. Die Konfiguration (config.py)
Zuerst definieren wir alle Konstanten an einem Ort.

Python
# config.py
ROUTER_HOST = "127.0.0.1"
ROUTER_PORT = 9999
AGENT_ALIAS = "stm"

# LM Studio Einstellungen
LM_STUDIO_URL = "http://localhost:1234/v1"
MODEL_ID = "local-model" # In LM Studio unter 'ID' zu finden

SYSTEM_PROMPT = """
Du bist der STM (Smart Trade Manager), ein Junior-Agent. 
Dein Boss ist 'human'. Antworte kurz, professionell und warte auf Anweisungen.
"""
2. Der Netzwerk-Client (network.py)
Dieses Modul übernimmt die gesamte TelChat-Logik: Verbindung, Registrierung und Heartbeats.

Python
import socket
import json
import time
import threading
from config import ROUTER_HOST, ROUTER_PORT, AGENT_ALIAS

class TelChatClient:
    def __init__(self, message_callback):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.callback = message_callback
        self.running = True

    def connect(self):
        self.sock.connect((ROUTER_HOST, ROUTER_PORT))
        # Phase 1: Registrierung laut Blueprint
        self.send_message("router", "registration", {"alias": AGENT_ALIAS})
        
        # Threads starten
        threading.Thread(target=self._receive_loop, daemon=True). प्रारंभ().start()
        threading.Thread(target=self._heartbeat_loop, daemon=True).start()

    def send_message(self, to, msg_type, data_obj):
        payload_str = json.dumps(data_obj)
        msg = {
            "from": AGENT_ALIAS,
            "to": to,
            "msg_type": msg_type,
            "timestamp": time.time(),
            "byte_count": len(payload_str.encode("utf-8")), #
            "data": data_obj
        }
        full_msg = (json.dumps(msg) + "\n").encode("utf-8") #
        self.sock.sendall(full_msg)

    def _receive_loop(self):
        buffer = ""
        while self.running:
            try:
                data = self.sock.recv(4096).decode("utf-8")
                if not data: break
                buffer += data
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.strip():
                        self.callback(json.loads(line))
            except Exception as e:
                print(f"Fehler beim Empfang: {e}")
                break

    def _heartbeat_loop(self):
        while self.running:
            time.sleep(45) # Sicherer Puffer vor dem 60s Watchdog
            self.send_message("router", "ack", {"status": "alive"})
3. Die KI-Schnittstelle (engine.py)
Hier nutzen wir die OpenAI-kompatible API von LM Studio.

Python
import requests
from config import LM_STUDIO_URL, SYSTEM_PROMPT, MODEL_ID

class LLMEngine:
    def generate_response(self, user_text):
        payload = {
            "model": MODEL_ID,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ],
            "temperature": 0.7
        }
        try:
            response = requests.post(f"{LM_STUDIO_URL}/chat/completions", json=payload)
            return response.json()['choices'][0]['message']['content']
        except Exception as e:
            return f"Fehler bei KI-Anfrage: {e}"
4. Der Haupt-Ablauf (main.py)
Dieses Skript verbindet die Teile. Es reagiert auf Nachrichten von human.

Python
from network import TelChatClient
from engine import LLMEngine
import time

engine = LLMEngine()

def on_message_received(msg):
    # Nur reagieren, wenn die Nachricht für uns ist und Daten enthält
    if msg.get("to") == "stm" and msg.get("msg_type") == "data":
        sender = msg.get("from")
        user_input = msg.get("data", {}).get("text", str(msg.get("data")))
        
        print(f"Nachricht von {sender} erhalten: {user_input}")
        
        # KI antworten lassen
        ai_reply = engine.generate_response(user_input)
        
        # Antwort zurückschicken
        client.send_message(sender, "data", {"text": ai_reply})

client = TelChatClient(on_message_received)

if __name__ == "__main__":
    print("STM Agent startet...")
    client.connect()
    
    # Programm am Laufen halten
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        client.running = False
        print("Agent beendet.")
Was dieser Code erfüllt (Checkliste):
Netzwerk: Nutzt TCP-Sockets auf Port 9999 mit Newline-Terminierung.

Protokoll: Implementiert das 6-Felder-Pflichtschema (from, to, msg_type, timestamp, byte_count, data).

Lebenszyklus: Führt die Registrierung sofort aus und hält die Verbindung durch Heartbeats stabil.

KI: Integriert LM Studio über die REST-API mit einem definierten System-Prompt.

Erweiterbarkeit: Die on_message_received-Funktion kann später leicht um Tool-Calls oder Scheduler-Prüfungen ergänzt werden.