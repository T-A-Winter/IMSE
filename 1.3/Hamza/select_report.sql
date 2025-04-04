-- Zeigt alle Benutzer ohne Filterung nach Prime-Status
SELECT
  Benutzer.Vorname,
  Benutzer.Nachname,
  Benutzer.GratisLieferung AS 'Prime Status',
  COUNT(OrderItem.OrderItemID) AS AnzahlGerichte,
  SUM(Gericht.Preis * OrderItem.Stückzahl) AS Gesamtpreis
FROM
  Benutzer
JOIN Warenkorb ON Benutzer.WarenkorbID = Warenkorb.WarenkorbID
JOIN OrderItem ON Warenkorb.WarenkorbID = OrderItem.WarenkorbID
JOIN Gericht ON OrderItem.GerichtID = Gericht.GerichtID
GROUP BY
  Benutzer.Vorname, Benutzer.Nachname, Benutzer.GratisLieferung;