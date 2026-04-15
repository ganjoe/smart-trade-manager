ID,Category,Title,Description,Covered By
F-SYS-010,System,TelChat Client Core,"Der Agent hält eine persistente TCP-Verbindung und nutzt das JSON-Schema (from, to, data, timestamp) zur Kommunikation.",-
F-SCH-020,Scheduler,Task Registration Tool,"Ein Werkzeug ermöglicht es dem Agenten, Dateinamen und Unix-Timestamps als ""Wiedervorlage"" in die Scheduler-Tabelle einzutragen.",-
F-SCH-030,Scheduler,Task Deletion Tool,"Der Agent kann geplante Einträge im Scheduler gezielt entfernen, wenn ein Vorgang abgeschlossen oder ungültig ist.",-
F-TIME-040,Market,Market Status Provider,Ein Werkzeug liefert den Echtzeit-Status (Open/Closed/Holiday) einer Börse basierend auf dem übergebenen Ticker-Symbol.,-
F-TIME-050,Market,Ticker-to-Exchange Resolver,Das System ordnet Ticker-Symbole (z.B. AAPL) automatisch der korrekten Heimatbörse und deren spezifischer Zeitzone zu.,-
F-FILE-060,File,Strategic Archiving,"Das System stellt eine Funktion bereit, um Merkzettel bei Beendigung eines Vorgangs vom Arbeits- in das Archivverzeichnis (""Trash"") zu verschieben.",-
F-FILE-070,File,State Persistence,Der Agent kann während der Bearbeitung Änderungen am Inhalt des aktuellen Merkzettels persistent in der JSON-Datei speichern.,-
F-MATH-080,Logic,Python Math Engine,Mathematische Berechnungen und boolesche Schwellenwert-Vergleiche werden in Python ausgeführt und das Ergebnis an das LLM zurückgegeben.,-
F-COM-090,Comm,Sync Expert Query,"Ein Werkzeug erlaubt es dem STM, den STA über den Router abzufragen (inkl. Marktdaten) und die Antwort in den Kontext zu laden.",-
F-UX-100,UX,Junior-Mode Confirmation,Jede operative Entscheidung (z.B. Benachrichtigung an User oder Löschung) erfordert im Junior-Modus ein explizites ACK von @human.,-
F-SYS-110,System,Context Injection,"Bei jedem Wakeup (durch Scheduler oder neue TelChat-Nachricht) wird dem Boss (LLM) der entsprechende Auslöser-Kontext übergeben.",-
F-MSG-120,Queue,Message Dispatcher,"Die Sekretärin (Python-Logik) puffert eingehende Nachrichten und reicht sie nacheinander zur Prüfung an den Boss (LLM) weiter, sobald dieser verfügbar ist.",-
F-FILE-130,File,Active Contracts Tool,"Ein Werkzeug erlaubt es dem Boss, eine Übersicht aller aktuell aktiven Verträge (Merkzettel) anzufordern, um die Gesamt-Situation zu überblicken.",-
F-FILE-140,File,Contract Creation Tool,"Ein Werkzeug erlaubt es dem Boss, die Sekretärin final anzuweisen, eine komplett neue Vertragsdatei (Merkzettel) im Dateisystem anzulegen.",-