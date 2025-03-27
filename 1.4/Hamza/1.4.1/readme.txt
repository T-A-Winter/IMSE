Erklärung zu den Schemas:

1. Benutzer-Dokument:
   - Enthält alle grundlegenden Benutzerinformationen
   - Das Prime-Objekt enthält alle wichtigen Informationen zur Prime-Mitgliedschaft
   - Durch die Einbettung können wir sofort erkennen, ob der Benutzer Prime-Vorteile hat
   - Der Warenkorb mit eingebetteten OrderItems zeigt direkt, dass keine Liefergebühr anfällt

2. PrimeKundenReport-Dokument:
   - Optimiert für die Abfrage "Prime aktivieren und bestellen"
   - Zeigt nur die relevanten Daten für den Report
   - Die Bestellungen werden mit 0.00 Liefergebühr angezeigt
   - Vorberechnete Aggregate ermöglichen schnelle Abfragen

Dieses Design unterstützt den Use Case "Prime aktivieren und bestellen" optimal, 
da der Prime-Status und die kostenlose Lieferung direkt erkennbar sind.