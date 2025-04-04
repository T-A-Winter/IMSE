-- App
CREATE TABLE App (
    AppID INTEGER AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Version VARCHAR(20) NOT NULL
);

-- Restaurant
CREATE TABLE Restaurant (
    RestaurantID INTEGER AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    OffenVon TIME,
    OffenBis TIME,
    Straße VARCHAR(255) NOT NULL,
    Ort VARCHAR(255) NOT NULL,
    PLZ INTEGER NOT NULL,
    AppID INTEGER,
    FOREIGN KEY (AppID) REFERENCES App(AppID)
);

-- Gericht
CREATE TABLE Gericht (
    GerichtID INTEGER AUTO_INCREMENT PRIMARY KEY,
    GerichtName VARCHAR(100) NOT NULL,
    Preis DECIMAL(6,2) NOT NULL,
    RestaurantID INTEGER,
    FOREIGN KEY (RestaurantID) REFERENCES Restaurant(RestaurantID)
);

-- Warenkorb
CREATE TABLE Warenkorb (
    WarenkorbID INTEGER AUTO_INCREMENT PRIMARY KEY,
    Erstelldatum DATETIME DEFAULT CURRENT_TIMESTAMP,
    RestaurantID INTEGER,
    Status VARCHAR(20) DEFAULT 'offen',
    FOREIGN KEY (RestaurantID) REFERENCES Restaurant(RestaurantID)
);

-- Benutzer 
CREATE TABLE Benutzer (
    BenutzerID INTEGER AUTO_INCREMENT PRIMARY KEY,
    Vorname VARCHAR(50) NOT NULL,
    Nachname VARCHAR(50) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    Straße VARCHAR(255) NOT NULL,
    Ort VARCHAR(255) NOT NULL,
    PLZ INTEGER NOT NULL,
    Passwort VARCHAR(100) NOT NULL,
    PromoCode VARCHAR(20),
    GratisLieferung BOOLEAN DEFAULT FALSE,
    AppID INTEGER,
    WarenkorbID INTEGER,
    EingeladenVon INTEGER,
    FOREIGN KEY (AppID) REFERENCES App(AppID),
    FOREIGN KEY (WarenkorbID) REFERENCES Warenkorb(WarenkorbID),
    FOREIGN KEY (EingeladenVon) REFERENCES Benutzer(BenutzerID)
);

-- Gast (IS-A Benutzer)
CREATE TABLE Gast (
    BenutzerID INTEGER PRIMARY KEY,
    SessionID INTEGER AUTO_INCREMENT,
    Ablaufdatum TIME
    FOREIGN KEY (BenutzerID) REFERENCES Benutzer(BenutzerID) ON DELETE CASCADE
);

-- PrimeKunde (IS-A Benutzer)
CREATE TABLE PrimeKunde (
    BenutzerID INTEGER PRIMARY KEY,
    Gebühr DECIMAL(5,2),
    GratisLieferung BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (BenutzerID) REFERENCES Benutzer(BenutzerID) ON DELETE CASCADE
);

-- OrderItem (schwache Entität)
CREATE TABLE OrderItem (
    OrderItemID INTEGER AUTO_INCREMENT,
    WarenkorbID INTEGER,
    RestaurantAnschrift VARCHAR(255),
    TotalPreis DECIMAL(8,2),
    Stückzahl INTEGER NOT NULL,
    GerichtID INTEGER,
    PRIMARY KEY (OrderItemID, WarenkorbID),
    FOREIGN KEY (WarenkorbID) REFERENCES Warenkorb(WarenkorbID) ON DELETE CASCADE,
    FOREIGN KEY (GerichtID) REFERENCES Gericht(GerichtID)
);

-- Lieferant
CREATE TABLE Lieferant (
    DienstID INTEGER AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    FahrzeugTyp ENUM('Auto', 'Fahrrad') NOT NULL,
    AppID INTEGER,
    FOREIGN KEY (AppID) REFERENCES App(AppID)
);

-- Mitglied (1:m-Beziehung zwischen App und PrimeKunde)
CREATE TABLE Mitglied (
    PrimeID INTEGER AUTO_INCREMENT PRIMARY KEY,
    BenutzerID INTEGER,
    FOREIGN KEY (BenutzerID) REFERENCES Benutzer(BenutzerID)
);

-- Bewertung (m:n-Beziehung zwischen Benutzer und Restaurant)
CREATE TABLE Bewertung (
    BenutzerID INTEGER,
    RestaurantID INTEGER,
    Bewertung INTEGER CHECK (Bewertung BETWEEN 1 AND 5),
    PRIMARY KEY (BenutzerID, RestaurantID),
    FOREIGN KEY (BenutzerID) REFERENCES Benutzer(BenutzerID) ON DELETE CASCADE,
    FOREIGN KEY (RestaurantID) REFERENCES Restaurant(RestaurantID) ON DELETE CASCADE
);

-- Bestellt (für die Beziehung zwischen Benutzer, Restaurant und Warenkorb)
CREATE TABLE Bestellt (
    BenutzerID INTEGER,
    RestaurantID INTEGER,
    WarenkorbID INTEGER,
    PRIMARY KEY (BenutzerID, RestaurantID, WarenkorbID),
    FOREIGN KEY (BenutzerID) REFERENCES Benutzer(BenutzerID) ON DELETE CASCADE,
    FOREIGN KEY (RestaurantID) REFERENCES Restaurant(RestaurantID) ON DELETE CASCADE,
    FOREIGN KEY (WarenkorbID) REFERENCES Warenkorb(WarenkorbID) ON DELETE CASCADE
);
