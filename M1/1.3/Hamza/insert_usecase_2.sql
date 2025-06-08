-- 1) Anna als Prime Kunde markieren
INSERT INTO PrimeKunde (BenutzerID, Gebühr, GratisLieferung)
VALUES (1, 9.99, TRUE);

-- 2) Eintrag in Mitglied Tabelle hinzufügen
INSERT INTO Mitglied (BenutzerID)
VALUES (1);

-- 3) GratisLieferung Flag im Benutzer setzen
UPDATE Benutzer
SET GratisLieferung = TRUE
WHERE BenutzerID = 1;

-- 4) Noch ein Gericht zum Warenkorb hinzufügen
INSERT INTO OrderItem (WarenkorbID, RestaurantAnschrift, TotalPreis, Stückzahl, GerichtID)
VALUES (1, 'Hauptstraße 10, 10115 Berlin', 8.50, 1, 1);