-- 1) App erstellen
INSERT INTO App (Name, Version) VALUES ('Lieferapp', '1.0');

-- 2) Restaurant erstellen
INSERT INTO Restaurant (Name, OffenVon, OffenBis, Straße, Ort, PLZ, AppID)
VALUES ('Lecker Imbiss', '10:00:00', '22:00:00', 'Hauptstraße 10', 'Berlin', 10115, 1);

-- 3) Gericht erstellen
INSERT INTO Gericht (GerichtName, Preis, RestaurantID)
VALUES ('Burger', 8.50, 1);

INSERT INTO Gericht (GerichtName, Preis, RestaurantID)
VALUES ('Pommes', 3.50, 1);

-- 4) Warenkorb erstellen
INSERT INTO Warenkorb (RestaurantID)
VALUES (1);

-- 5) Benutzer erstellen (noch kein Prime Kunde)
INSERT INTO Benutzer (Vorname, Nachname, Email, Straße, Ort, PLZ, Passwort, PromoCode, GratisLieferung, AppID, WarenkorbID)
VALUES ('Anna', 'Schmidt', 'anna.schmidt@example.com', 'Musterweg 5', 'Berlin', 10115, 'passwort123', 'NEUKUNDE20', FALSE, 1, 1);

-- 6) OrderItem erstellen (Burger und Pommes)
INSERT INTO OrderItem (WarenkorbID, RestaurantAnschrift, TotalPreis, Stückzahl, GerichtID)
VALUES (1, 'Hauptstraße 10, 10115 Berlin', 8.50, 1, 1);

INSERT INTO OrderItem (WarenkorbID, RestaurantAnschrift, TotalPreis, Stückzahl, GerichtID)
VALUES (1, 'Hauptstraße 10, 10115 Berlin', 3.50, 1, 2);