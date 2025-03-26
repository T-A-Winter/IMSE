
-- 1) App erstellen
INSERT INTO App (Name, Version) VALUES ('Lieferapp', '1.0');

-- 2) Restaurant erstellen
INSERT INTO Restaurant (Name, OffenVon, OffenBis, Straße, Ort, PLZ, AppID)
VALUES ('Muster Restaurant', '11:00:00', '21:00:00', 'Hauptstraße 5', 'MusterOrt', 1234, 1);

-- 3) Gericht erstellen
INSERT INTO Gericht (GerichtName, Preis, RestaurantID)
VALUES ('Pizza', 7.0, 1);

-- 4) Warenkorb erstellen
INSERT INTO Warenkorb (RestaurantID)
VALUES (1);

-- 5) Benutzer erstellen
INSERT INTO Benutzer (Vorname, Nachname, Email, Straße, Ort, PLZ, Passwort, AppID, WarenkorbID)
VALUES ('Max', 'Mustermann', 'Mustermann@mustermail.com', 'Musterstraße 1', 'MusterOrt', 1234, 'passwort123', 1, 1);

-- 6) OrderItem erstellen (2x Pizza)
INSERT INTO OrderItem (WarenkorbID, RestaurantAnschrift, TotalPreis, Stückzahl, GerichtID)
VALUES (1, 'Hauptstraße 5', 14.0, 2, 1);
