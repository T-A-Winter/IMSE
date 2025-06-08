Erklärung zu den Schemas:

Der Benutzer spielt in dem Usecase die Größte rolle.

Das Schema Benutzer: 

Benutzer hat eingebettet die App (als meta data)
und den Warenkorb. 

Im Warenkorb ist eingebettet das Restaurant und
die OrderItems. In einem OrderItem is ein Gericht
eingebettet. 

Das Schema Restaurant:

Hier reicht es nur die App und die Gerichte
einzubetten. 

Falls man jetzt später den Report sehen will aus
1.3.2


SELECT
  Benutzer.Vorname,
  Benutzer.Nachname,
  Gericht.GerichtName,
  OrderItem.Stückzahl,
  Gericht.Preis,
  (Gericht.Preis * OrderItem.Stückzahl) AS Gesamtpreis,
  Restaurant.Name AS RestaurantName
FROM
  Benutzer
JOIN OrderItem ON Benutzer.WarenkorbID = OrderItem.WarenkorbID
JOIN Gericht ON OrderItem.GerichtID = Gericht.GerichtID
JOIN Restaurant ON Gericht.RestaurantID = Restaurant.RestaurantID
WHERE
  Restaurant.Name = 'Muster Restaurant';


Gibt es ein extra report Schema:

Hier sehen wir uns ein Restaurant an. Eingebettet sind die Bestellungen.
Darauß lässt sich ein Report erstellen. 