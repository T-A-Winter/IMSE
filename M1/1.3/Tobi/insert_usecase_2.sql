
-- Gericht Spaghetti hinzufügen
INSERT INTO Gericht (GerichtName, Preis, RestaurantID)
VALUES ('Spaghetti', 9.0, 1);

-- Neuen Warenkorb erstellen
INSERT INTO Warenkorb (RestaurantID)
VALUES (1);

-- Neuen Benutzer erstellen
INSERT INTO Benutzer (Vorname, Nachname, Email, Straße, Ort, PLZ, Passwort, AppID, WarenkorbID)
VALUES ('Erika', 'Musterfrau', 'erika@muster.com', 'Blumenweg 3', 'MusterOrt', 1234, 'erika_pw', 1, 2);

-- OrderItem für Spaghetti
INSERT INTO OrderItem (WarenkorbID, RestaurantAnschrift, TotalPreis, Stückzahl, GerichtID)
VALUES (2, 'Hauptstraße 5', 9.0, 1, 2);
