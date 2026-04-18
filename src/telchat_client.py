import socket
import json
import threading
import time
from typing import Callable, Any, Optional
from .models import AgentConfig, TelChatMessage

class TelChatClient:
    """
    TCP Client for the TelChat Router communication.
    Inherits 'Secretary' duties: connection, registration, and heartbeat.
    """
    def __init__(self, config: AgentConfig):
        self.config = config
        self.sock: Optional[socket.socket] = None
        self._is_running = False

    def connect_and_register(self) -> bool:
        """Establishes connection and registers the agent alias immediately."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Set timeout to avoid infinite block during connect
            self.sock.settimeout(10.0) 
            self.sock.connect((self.config.router_host, self.config.router_port))
            # Remove timeout for blocking recv
            self.sock.settimeout(None)
            
            self._is_running = True
            
            # Blueprint Phase 1: Registration
            self.send_message("router", "registration", {"alias": self.config.alias})
            
            # Blueprint Phase 2: Heartbeat (Wait 50s)
            threading.Thread(target=self._heartbeat_loop, daemon=True).start()
            
            print(f"[*] Agent '{self.config.alias}' registered at {self.config.router_host}:{self.config.router_port}")
            return True
        except Exception as e:
            print(f"[!] Connection failed for {self.config.alias}: {e}")
            return False

    def _heartbeat_loop(self):
        """Sends a heartbeat every 20 seconds to keep the router connection alive (60s watchdog)."""
        while self._is_running:
            time.sleep(20)
            if self._is_running:
                try:
                    # Send heartbeat to self instead of "router" to avoid connection errors
                    self.send_message(self.config.alias, "ack", {"ping": "pong"})
                except Exception:
                    self._is_running = False
                    break

    def send_message(self, to: str, msg_type: str, data: dict) -> None:
        """Serializes and sends a TelChat message over the socket."""
        if not self.sock or not self._is_running:
            return
        
        try:
            msg = TelChatMessage(
                sender=self.config.alias,
                to=to,
                msg_type=msg_type,
                data=data
            )
            raw_data = msg.to_json_line().encode("utf-8")
            self.sock.sendall(raw_data)
        except Exception as e:
            print(f"[!] Send error: {e}")
            self._is_running = False

    def listen(self, message_handler: Callable[[TelChatMessage], None]) -> None:
        """
        Receives messages line by line and passes them to the handler.
        This is a blocking operation.
        """
        buffer = ""
        while self._is_running:
            try:
                chunk = self.sock.recv(4096).decode("utf-8")
                if not chunk:
                    print(f"[*] Connection lost for {self.config.alias}.")
                    break
                
                buffer += chunk
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line.strip():
                        try:
                            msg = TelChatMessage.from_json(line)
                            # Invoke the Boss's handler
                            message_handler(msg)
                        except json.JSONDecodeError:
                            print(f"[!] Malformed message received: {line}")
            except Exception as e:
                if self._is_running:
                    print(f"[!] Receive error: {e}")
                break
        
        self._is_running = False
        if self.sock:
            self.sock.close()
            self.sock = None

    def stop(self):
        """Cleanly stops the client."""
        self._is_running = False
        if self.sock:
            self.sock.close()
            self.sock = None
