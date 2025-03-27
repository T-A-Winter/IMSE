Meine Annahmen:

Der "Prime aktivieren und Bestellen" Use Case funktioniert gut mit 
eingebettetem Prime-Status im Benutzer-Dokument. Das macht Front- und 
Backend-Entwicklung einfacher, weil man direkt sieht, ob Gratislieferung
verfügbar ist oder nicht.

Für den Report wäre es ziemlich ineffizient, alle Benutzer zu durchsuchen.
Deshalb hab ich ein extra PrimeKundenReport-Dokument erstellt - das 
enthält nur Prime-Mitglieder und spart uns viel Rechenzeit.

Frage:

Analyze how changes in the number of database operations of your USE CASE (e.g., more
frequent reads or writes) would affect your NoSQL data structure. Would you need to adjust
document embedding, referencing, or indexing strategies? Explain your reasoning.

Ich denke, das Design hält auch mehr Operationen gut aus:
- Prime-Aktivierungen betreffen immer nur ein Dokument
- Bei Bestellungen brauchen wir keine komplexen Verknüpfungen
- Der Report ist schon optimiert durch die Vorfilterung

Eine Anpassung wäre erst nötig, wenn Kunden wirklich viele Bestellungen 
anhäufen. Dann könnte man ältere Bestellungen auslagern, aber für jetzt
passt das Design gut.