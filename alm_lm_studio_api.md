# LM Studio REST API - System Context & Capabilities Reference

Diese Dokumentation definiert die Schnittstellen und Fähigkeiten der lokalen LM Studio REST API (Standard-Endpoint: `http://localhost:1234`). Sie dient als Kontext für Code-Generierung und Tool-Orchestrierung.

## 1. API Architektur & Endpunkte

Das System bietet zwei parallele Schnittstellen-Paradigmen:

*   **Native v1 API (`/api/v1/*`)**: Ausgelegt für Modell- und Ressourcenmanagement, zustandsbehaftete Chats (Stateful) und serverseitiges Model Context Protocol (MCP).
*   **OpenAI Kompatibilität (`/v1/*`)**: Ausgelegt für zustandslose Inferenz, Client-seitiges Function Calling (Tools) und Strict Structured Outputs.

## 2. Ressourcen- und Modellmanagement (Native API)

RAM und VRAM müssen aktiv durch explizites Laden und Entladen verwaltet werden.

### Modelle auflisten
**Endpoint:** `GET /api/v1/models`  
Liefert ein Array verfügbarer Modelle inkl. `size_bytes`, `type` (`llm` oder `embedding`) und `quantization`.

### Modell in den Speicher laden
**Endpoint:** `POST /api/v1/models/load`  
**Payload:**
```json
{
  "model": "<model_id>",
  "context_length": 8192,
  "offload_kv_cache_to_gpu": true
}
```
**Verhalten:** Die `context_length` bestimmt den VRAM-Bedarf. Bei OOM-Fehlern (Out of Memory) muss dieser Wert reduziert werden. Liefert eine `instance_id` zurück.

### Modell entladen (VRAM Freigabe)
**Endpoint:** `POST /api/v1/models/unload`  
**Payload:**
```json
{
  "instance_id": "<instance_id>"
}
```
**Wichtig:** Zwingend erforderlich nach Abschluss eines Tasks, um Memory Leaks zu vermeiden.

### Modell herunterladen
**Endpoint:** `POST /api/v1/models/download`  
Blockiert nicht. Status-Polling via `GET /api/v1/models/download/status/{job_id}`.

## 3. Native Chat & Model Context Protocol (/api/v1/chat)

Dieser Endpunkt weicht vom OpenAI-Standard ab und bietet native Erweiterungen.

*   **Zustandsbehaftet (Stateful):** Die API speichert den Konversationsverlauf. Ein Request liefert ein `response_id` Feld. Für Multi-Turn-Interaktionen wird diese ID als `previous_response_id` im neuen Request mitgesendet, anstatt das `messages` Array neu zu übergeben.
*   **Streaming-Ereignisse:** Bei `stream: true` (SSE) liefert der Server deterministische Events: `model_load.progress`, `prompt_processing.progress`, `message.delta` (Textfragmente) und `chat.end` (inkl. Token-Statistiken).
*   **Netzwerk-Werkzeuge (MCP):** Externe Tools werden als Server im `integrations` Array übergeben.  
    **Beispiel Payload für ephemere Server:**
    ```json
    {
      "type": "ephemeral_mcp",
      "server_url": "...",
      "allowed_tools": ["tool_name"]
    }
    ```
    Die API übernimmt die Netzwerkanfrage und injiziert das Resultat automatisch in den Prompt.

## 4. Lokaler Tool Use & Structured Output (/v1/chat/completions)

Zur Nutzung bestehender Agent-Frameworks (Zustandslos).

### Function Calling / Tools
*   Definition lokaler Funktionen als JSON-Schema im Array `tools`.
*   Das Modell generiert Tool-Aufrufe, welche von der API im Feld `response.choices.message.tool_calls` strukturiert zurückgegeben werden.
*   **Multi-Turn Flow:** Nach der lokalen Ausführung des Codes müssen sowohl der ursprüngliche `tool_call` als auch das Resultat als neues Message-Objekt (role: "tool", inkl. `tool_call_id`) dem Array hinzugefügt und ein erneuter Request gesendet werden.

### Structured Output (Deterministisches JSON)
*   Wird erzwungen durch die Definition eines JSON-Schemas im Parameter `response_format`.
*   Damit Modelle das Schema verlässlich einhalten, muss das Schema `strict: true` enthalten und in allen Objekten zwingend `additionalProperties: false` deklarieren.

## 5. Embeddings & Vektor-Generierung (/v1/embeddings)

*   **Voraussetzung:** Ein Modell mit `type: "embedding"` muss zuvor via `/api/v1/models/load` geladen sein.
*   **Chunking & VRAM:** Die konfigurierte `context_length` des Embedding-Modells limitiert die Input-Größe strikt. Text-Dokumente müssen auf Client-Seite in Chunks zerlegt werden, die dieses Limit (z. B. 1024 oder 4096 Tokens) nicht überschreiten, um Abstürze zu verhindern.