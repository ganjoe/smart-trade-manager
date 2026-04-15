import sys
import os
from .models import AgentConfig, TelChatMessage
from .telchat_client import TelChatClient
from .llm_service import LLMService
from . import tools

class SmartTradeManagerApp:
    """
    Main Application class for the Smart Trade Manager.
    Integrates the TelChatClient (Secretary) and LLMService (Boss).
    """
    def __init__(self, config_path: str = "config.json"):
        print(f"[*] Initializing Smart Trade Manager...")
        try:
            # Task [T-001/T-004]: Load dynamic config
            self.config = AgentConfig.from_file(config_path)
            print(f"[*] Config loaded from {config_path}")
        except Exception as e:
            print(f"[!] Critical Error: Failed to load config: {e}")
            sys.exit(1)
            
        self.client = TelChatClient(self.config)
        self.llm = LLMService(self.config)
        
        # Initialize directory structures for the Secretary tools
        tools.ensure_directories()

    def on_message_received(self, msg: TelChatMessage) -> None:
        """
        Callback triggered by the 'Secretary' (TelChatClient) when a 
        new message arrives from the router.
        """
        # Logic: Only handle 'data' messages intended for us
        # We ignore ACKs and system notifications for now.
        if msg.msg_type == "data" and msg.to == self.config.alias:
            sender = msg.sender
            
            # Extract text from message data
            # Typically looks like {"text": "Hello"} or similar data object
            data_content = msg.data
            input_text = ""
            if isinstance(data_content, dict):
                input_text = data_content.get("text") or data_content.get("msg") or str(data_content)
            else:
                input_text = str(data_content)
            
            print(f"[*] Received message from '{sender}': {input_text}")
            
            # Phase: Analysis (Invoke the 'Boss')
            ai_reply = self.llm.generate_response(input_text)
            
            print(f"[*] Sending AI response to '{sender}'")
            
            # Phase: Communication (Instruct the 'Secretary' to reply)
            self.client.send_message(
                to=sender,
                msg_type="data",
                data={"text": ai_reply}
            )
        elif msg.msg_type == "error":
            print(f"[!] Router reported an error: {msg.data.get('error')}")

    def start(self):
        """Starts the agent loop."""
        print(f"[*] Starting agent loop for '{self.config.alias}'...")
        
        # Connect to the router
        if self.client.connect_and_register():
            try:
                # Use listen() which blocks until connection is lost or stopped
                self.client.listen(self.on_message_received)
            except KeyboardInterrupt:
                print("\n[*] Manual shutdown requested.")
            finally:
                self.client.stop()
                print("[*] Agent stopped.")
        else:
            print("[!] Could not connect to the TelChat router. Please check your config and connection.")

def main():
    # Allow overriding config via environment variable for Docker
    config_file = os.environ.get("STM_CONFIG_FILE", "config.json")
    app = SmartTradeManagerApp(config_file)
    app.start()

if __name__ == "__main__":
    main()
