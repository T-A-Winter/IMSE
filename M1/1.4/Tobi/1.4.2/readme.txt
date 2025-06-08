Meine Annahmen:

Das Dokument für Benutzer und Restaurant hilft uns später im erstellen
der Front und Backend da Warenkorb, Restautant und OrderItem mit 
Gerichten bereits eingebettet sind. Für das Reporting kann man 
das Dokument nur schlecht verwenden aus folgenden Grund:

Für müssen über N Benutzer iterieren und hier im Warenkorb nach
dem richtigen Restaurant filtern. Das Hat 3*N Vergleichsoperationen.

Deswegen hab ich ein Reporting Dokument das schon nach dem Restaurant
vorgefiltert ist. Hier braucht man dann nur noch über ein Subset der 
Totalen Benutzer iterieren. 

Frage:

Analyze how changes in the number of database operations of your USE CASE (e.g., more
frequent reads or writes) would affect your NoSQL data structure. Would you need to adjust
document embedding, referencing, or indexing strategies? Explain your reasoning.

Mit dem reporting Dokument braucht man keine neuen Strategien.
Es hat exact die Informationen die man für den Report braucht. 
