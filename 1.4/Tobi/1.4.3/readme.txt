Frage:

Discuss your NoSQL design based on these five rules of thumb for document-based NoSQL
databases. Provide brief, individual explanations on how you applied each rule to your design.
1. Favor embedding unless there is a compelling reason not to.
2. The need to access an object on its own is a compelling reason not to embed it
3. High-cardinality arrays are a compelling reason not to embed.
4. Consider the write/read ratio of a collection/document when denormalizing.
5. Structure your data to match the ways that your application queries and updates it.

1. Im Benutzer Dokument sieht man ganz gut wie ich diese Regel angewendet
habe. Hier hat man alle nötigen Informationen um eine Bestellung anzulegen. 
Man kann in weiteren Zügen andere Dokumente "Querien" um eventuelle checks zu machen.
Wie z.b.: existiert das Restauerant mit diesen Gerichten.

Im Reporting Dokument wurde auch embedding bevorzugt, da man hier nur noch
ein Subset der Benutzer betrachten muss.

2. Ich Eingebettet keine Benutzer in Restaurant obwohl ich Resturant in 
Benutzer eingebette. Der Grund dafür - man müsste den Benutzer sonst
an zwei Orten aktuell hatlen. Restaurant Daten ändern sich nicht 
so häufig.

3. Diese Regel wird bei mir im moment noch etwas vernachlässigt. 
Ich hab versucht mit dem Reporting Dokument nur ein Subset statt
alle einträge von Benutzer einzubetten als "Bestellung".

4. Beim Benutzer wird sich die Bestellung (OrderItem) oft ändern und beim 
Reporting wird die "Bestellung" oft aktuallisiert. Hingegen wird die App 
als meta Datum eher selten neu geschrieben, deswegen ist diese Entitie auch
eingebettet statt als Eigenes Dokument. 

5. Benutzer ist so ausgelegt das man ganz leicht Front und Backend darauf 
aufbauen kann. Mit dem Reporting Dokument decke ich den Usecase ab. 