Frage:

Discuss your NoSQL design based on these five rules of thumb for document-based NoSQL
databases. Provide brief, individual explanations on how you applied each rule to your design.
1. Favor embedding unless there is a compelling reason not to.
2. The need to access an object on its own is a compelling reason not to embed it
3. High-cardinality arrays are a compelling reason not to embed.
4. Consider the write/read ratio of a collection/document when denormalizing.
5. Structure your data to match the ways that your application queries and updates it.

1. Das Embedding vom Prime-Status war naheliegend - spart mir Abfragen und zeigt sofort,
ob jemand ohne Liefergebühr bestellen kann. Warum kompliziert, wenn's auch einfach geht?

2. Restaurants hab ich bewusst separat gelassen. Die werden von zu vielen Kunden genutzt 
und ändern sich kaum. Wäre Unsinn, die in jedem Benutzer zu duplizieren.

3. Klar, wenn jemand wie verrückt bestellt, könnte das Warenkorb-Objekt irgendwann zu groß werden.
 Aber ehrlich - für unseren Kurs und den Use Case ist das völlig ausreichend.

4. Mein Design berücksichtigt, dass wir den Prime-Status zig-mal lesen, aber nur selten ändern.
 Der Report ist bewusst redundant angelegt - manchmal muss man halt Speicherplatz opfern, um Zeit zu sparen.

5. Hab das Schema praktisch vom Workflow abgeleitet: erst Prime aktivieren, dann bestellen.
 Im Benutzer-Dokument ist alles, was dieser Ablauf braucht, und der Report zeigt genau die Infos, die wir für die Auswertung brauchen.