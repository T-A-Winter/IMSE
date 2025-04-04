-- 1) App erstellen
INSERT INTO App (Name, Version) VALUES ('Lieferapp', '1.0');

-- 2) Restaurant erstellen
INSERT INTO Restaurant (Name, OffenVon, OffenBis, Straße, Ort, PLZ, AppID)
VALUES ('Lecker Imbiss', '10:00:00', '22:00:00', 'Hauptstraße 10', 'Berlin', 10115, 1);

-- 3) Gerichte erstellen
INSERT INTO Gericht (GerichtName, Preis, RestaurantID)
VALUES ('Burger', 8.50, 1);

INSERT INTO Gericht (GerichtName, Preis, RestaurantID)
VALUES ('Pommes', 3.50, 1);

-- 4) Warenkörbe erstellen
INSERT INTO Warenkorb (RestaurantID)
VALUES (1);

INSERT INTO Warenkorb (RestaurantID)
VALUES (1);

-- 5) Benutzer erstellen (normale Kunden)
INSERT INTO Benutzer (Vorname, Nachname, Email, Straße, Ort, PLZ, Passwort, PromoCode, GratisLieferung, AppID, WarenkorbID)
VALUES ('Anna', 'Schmidt', 'anna.schmidt@example.com', 'Musterweg 5', 'Berlin', 10115, 'passwort123', 'NEUKUNDE20', FALSE, 1, 1);

INSERT INTO Benutzer (Vorname, Nachname, Email, Straße, Ort, PLZ, Passwort, PromoCode, GratisLieferung, AppID, WarenkorbID)
VALUES ('Max', 'Müller', 'max.mueller@example.com', 'Berliner Str. 12', 'Berlin', 10117, 'maxPw456', NULL, TRUE, 1, 2);

-- 6) Max als Prime-Kunde eintragen (ist bereits ein Prime-Kunde)
INSERT INTO PrimeKunde (BenutzerID, Gebühr, GratisLieferung)
VALUES (2, 9.99, TRUE);

INSERT INTO Mitglied (BenutzerID)
VALUES (2);

-- 7) OrderItems erstellen (beide Kunden bestellen das Gleiche)
-- Anna's Bestellung
INSERT INTO OrderItem (WarenkorbID, RestaurantAnschrift, TotalPreis, Stückzahl, GerichtID)
VALUES (1, 'Hauptstraße 10, 10115 Berlin', 8.50, 1, 1);

INSERT INTO OrderItem (WarenkorbID, RestaurantAnschrift, TotalPreis, Stückzahl, GerichtID)
VALUES (1, 'Hauptstraße 10, 10115 Berlin', 3.50, 1, 2);

-- Max's Bestellung
INSERT INTO OrderItem (WarenkorbID, RestaurantAnschrift, TotalPreis, Stückzahl, GerichtID)
VALUES (2, 'Hauptstraße 10, 10115 Berlin', 8.50, 1, 1);

INSERT INTO OrderItem (WarenkorbID, RestaurantAnschrift, TotalPreis, Stückzahl, GerichtID)
VALUES (2, 'Hauptstraße 10, 10115 Berlin', 3.50, 1, 2);