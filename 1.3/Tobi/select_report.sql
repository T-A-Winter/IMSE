
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
