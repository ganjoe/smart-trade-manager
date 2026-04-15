# IMP_sprint_plan: Smart Trade Manager (Basis-Kommunikation)

*Basierend auf den Prinzipien des Senior Software Architects.*

## PART 1: The System Skeleton (Shared Context)

Dieses Skeleton definiert die abstrakte Struktur, die Datentypen und Schnittstellen. Alle Kern-Parameter sind extern in eine Dateistruktur (`config.json`) ausgelagert, um den späteren Docker-Betrieb flexibel zu gestalten (sodass man Parameter wie Router-IP und LM Studio-IP reinmappen kann).

```python
from dataclasses import dataclass, field
from typing import Dict, Any, Callable
import time
import json
import os

@dataclass
class AgentConfig:
    """Konfiguration für den Agenten (wird aus config.json geladen)"""
    alias: str
    router_host: str
    router_port: int
    llm_base_url: str
    llm_model_name: str
    system_prompt: str

    @classmethod
    def from_file(cls, path: str = "config.json") -> "AgentConfig":
        """Lädt die Konfiguration aus einer JSON-Datei."""
        pass

@dataclass
class TelChatMessage:
    """Standardisiertes Datenobjekt gemäß TelChat-Blueprint"""
    sender: str
    to: str
    msg_type: str
    data: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    
    def to_json_line(self) -> bytes:
        """Wandelt das Objekt in einen TelChat-kompatiblen, UTF-8 codierten JSON-String um (mit \n am Ende)."""
        pass
```

---

## PART 2: Implementation Work Orders

Hier sind die isolierten Arbeitsanweisungen (Work Orders) für die Junior-Agents dokumentiert. Im ersten Sprint geht es um Konfiguration, TelChat-Anbindung, LLM-Antworten und das finale Docker-Packaging.

### Task ID: [T-001]
**Target File:** `src/models.py`
**Description:** Implementierung der streng typisierten Datenmodelle und Konfiguration.
**Context:** Umfasst die Klassen `AgentConfig` und `TelChatMessage` aus dem Skeleton.
**Code Stub (MANDATORY):**
```python
from dataclasses import dataclass, field
from typing import Dict, Any
import time
import json
import os

@dataclass
class AgentConfig:
    alias: str
    router_host: str
    router_port: int
    llm_base_url: str
    llm_model_name: str
    system_prompt: str

    @classmethod
    def from_file(cls, path: str = "config.json") -> "AgentConfig":
        # TODO: Implementiere das Lesen der JSON Datei
        pass

@dataclass
class TelChatMessage:
    sender: str
    to: str
    msg_type: str
    data: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)

    def to_json_line(self) -> bytes:
        # TODO: Implementiere Serialisierung
        pass
```
**Algo/Logic Steps:**
1. `AgentConfig.from_file`: Lese `path` mit `json.load`. Bei `FileNotFoundError` werfe einen sauberen Fehler. Instanziiere die Klasse (`cls(**data)`).
2. `TelChatMessage.to_json_line`: Erstelle das standardisierte Dict `{"from": self.sender, "to": self.to, "msg_type": self.msg_type, "timestamp": self.timestamp, "data": self.data}`. Konvertiere das `data`-Dictionary temporär zu einem JSON-String, um die UTF-8 Bytezahl als `byte_count` Feld in das Haupt-Dictionary aufzunehmen. Konvertiere alles zu JSON, hänge ein `\n` ans Ende, wandle es in Bytes (`encode('utf-8')`) um und returne.
**Edge Cases:** Keine Besonderheiten.

---

### Task ID: [T-002]
**Target File:** `src/telchat_client.py`
**Description:** TCP-Socket Client für die asynchrone Kommunikation mit dem TelChat Router (Die Infrastruktur der "Sekretärin").
**Context:** Verwendet `TelChatMessage` und `AgentConfig` aus `models.py`.
**Code Stub (MANDATORY):**
```python
import socket
import json
from typing import Callable, Any
from .models import AgentConfig, TelChatMessage

class TelChatClient:
    def __init__(self, config: AgentConfig):
        self.config = config
        self.sock: socket.socket | None = None
        self._is_running = False

    def connect_and_register(self) -> bool:
        """ Verbindet zum Router und sendet die initiale msg_type: 'registration'. """
        pass

    def send_message(self, to: str, msg_type: str, data: dict) -> None:
        """ Baut eine TelChatMessage und versendet diese über den Socket. """
        pass

    def listen(self, message_handler: Callable[[TelChatMessage], None]) -> None:
        """ Blockierender Loop, der einkommende Zeilen liest und an den Handler übergibt. """
        pass
```
**Algo/Logic Steps:**
1. `connect_and_register`: Öffne `socket(AF_INET, SOCK_STREAM)`. Verbinde zu `router_host` & `router_port`. Sende eine initiale Registrierung: `send_message("router", "registration", {"alias": self.config.alias})`. Setze `_is_running = True`.
2. `listen`: Eingehende Pakete empfangen (`recv`) und per Buffer an `\n` splitten. Einzelne JSON Strings per `json.loads` verarbeiten, in `TelChatMessage` Objekte verpacken und `message_handler(msg)` aufrufen.
**Edge Cases:**
- System-`ACKs` oder `error`-Nachrichten vom Router abfangen. (Errors gerne in stdout loggen).

---

### Task ID: [T-003]
**Target File:** `src/llm_service.py`
**Description:** Wrapper für den API-Aufruf zu LM Studio über den openai client.
**Context:** Nutzt das offizielle `openai` pip-Package, injiziert System-Prompts aus der Config.
**Code Stub (MANDATORY):**
```python
from openai import OpenAI
from .models import AgentConfig

class LLMService:
    def __init__(self, config: AgentConfig):
        self.config = config
        self.client = OpenAI(base_url=self.config.llm_base_url, api_key="lm-studio")

    def generate_response(self, user_text: str) -> str:
        """ Befragt das Modell und liefert den reinen Antworttext. """
        pass
```
**Algo/Logic Steps:**
1. Stelle den `system`-Prompt auf `self.config.system_prompt` (innerhalb der `messages`-List).
2. Hänge den `user_text` an.
3. Führe den synchronen ChatCompletions-Call aus. Modelname=`self.config.llm_model_name`.
4. Gib `response.choices[0].message.content` zurück.
**Edge Cases:** Catch alle `openai` API-ConnectionErrors (z.B. wenn LM Studio noch bootet).

---

### Task ID: [T-004]
**Target File:** `src/main.py`
**Description:** App-Orchestrierung (Vereinigung von Boss und Sekretärin). Lädt die dynamische config.json Datei.
**Context:** Importiert `AgentConfig`, `TelChatClient` und `LLMService`. 
**Code Stub (MANDATORY):**
```python
import sys
from .models import AgentConfig
from .telchat_client import TelChatClient
from .llm_service import LLMService

class SmartTradeManagerApp:
    def __init__(self, config_path: str = "config.json"):
        try:
            self.config = AgentConfig.from_file(config_path)
        except Exception as e:
            print(f"Failed to load config: {e}")
            sys.exit(1)
            
        self.client = TelChatClient(self.config)
        self.llm = LLMService(self.config)

    def on_message_received(self, msg) -> None:
        pass

    def start(self):
        pass

if __name__ == "__main__":
    SmartTradeManagerApp().start()
```
**Algo/Logic Steps:**
1. `start`: Rufe `self.client.connect_and_register()` auf. Danach blockierend `self.client.listen(self.on_message_received)`.
2. `on_message_received`: Wenn `msg.msg_type == "data"`, lies den Text aus `msg.data`, hol dir über `self.llm.generate_response()` eine Antwort vom LLM und sende diese mit `self.client.send_message` als "data" formatierte Antwort an `msg.sender` zurück.

---

### Task ID: [T-005]
**Target Files:** `Dockerfile`, `requirements.txt`, `config.example.json`
**Description:** Containerisierung und Dependency-Management.
**Context:** Das Programm ist eine reine Hintergrundapplikation (keine freigegebenen Ports notwendig).
**Algo/Logic Steps:**
1. **requirements.txt**: Füge das `openai` Paket hinzu.
2. **Dockerfile**: Nutze `FROM python:3.11-slim` (oder neuer). 
   - Initialisiere das working directory `/app`
   - Kopiere `requirements.txt` -> `pip install -r`
   - Kopiere den Ordner `src/` nach `/app/src/`
   - Definiere das Startkommando: `CMD ["python", "-m", "src.main"]`
3. **config.example.json**: Erstelle eine JSON-Vorlage. Hinweis an die Benutzer: Im Docker-Umfeld muss die `router_host` IP und `llm_base_url` auf `host.docker.internal` (bei Docker Desktop) oder die statische IP des Hosts zeigen, um auf die Socket/API zugreifen zu können!
