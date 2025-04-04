SELECT
  Benutzer.Vorname,
  Benutzer.Nachname,
  CASE WHEN Benutzer.GratisLieferung = 1 THEN 'Prime' ELSE 'Standard' END AS 'Kunden-Status',
  COUNT(OrderItem.OrderItemID) AS AnzahlGerichte,
  SUM(Gericht.Preis * OrderItem.Stückzahl) AS Warenwert,
  CASE WHEN Benutzer.GratisLieferung = 1 THEN 0.00 ELSE 3.99 END AS Liefergebühr,
  SUM(Gericht.Preis * OrderItem.Stückzahl) + 
    CASE WHEN Benutzer.GratisLieferung = 1 THEN 0.00 ELSE 3.99 END AS Gesamtpreis
FROM
  Benutzer
JOIN Warenkorb ON Benutzer.WarenkorbID = Warenkorb.WarenkorbID
JOIN OrderItem ON Warenkorb.WarenkorbID = OrderItem.WarenkorbID
JOIN Gericht ON OrderItem.GerichtID = Gericht.GerichtID
GROUP BY
  Benutzer.Vorname, Benutzer.Nachname, Benutzer.GratisLieferung
ORDER BY
  Benutzer.Nachname;