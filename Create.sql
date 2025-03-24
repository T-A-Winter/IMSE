-- Benutzer
CREATE TABLE Benutzer (
    BenutzerID INTEGER PRIMARY KEY,
    Vorname VARCHAR(50) NOT NULL,
    Nachname VARCHAR(50) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    Adresse VARCHAR(100) NOT NULL,
    Passwort VARCHAR(100) NOT NULL,
    PromoCode VARCHAR(20)
);

-- PrimeKunde (Implementierung der IS-A-Beziehung)
CREATE TABLE PrimeKunde (
    BenutzerID INTEGER PRIMARY KEY,
    Gebühr DECIMAL(5,2),
    GratisLieferung BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (BenutzerID) REFERENCES Benutzer(BenutzerID) ON DELETE CASCADE
);

-- Restaurant 
CREATE TABLE Restaurant (
    RestaurantID INTEGER PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Anschrift VARCHAR(255) NOT NULL,
    Öffnungszeiten_Von TIME,
    Öffnungszeiten_Bis TIME
);

-- App 
CREATE TABLE App (
    AppID INTEGER PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Version VARCHAR(20) NOT NULL
);

-- Gericht 
CREATE TABLE Gericht (
    GerichtID INTEGER PRIMARY KEY,
    GerichtName VARCHAR(100) NOT NULL,
    Preis DECIMAL(6,2) NOT NULL,
    RestaurantID INTEGER,
    FOREIGN KEY (RestaurantID) REFERENCES Restaurant(RestaurantID)
);

-- Warenkorb 
CREATE TABLE Warenkorb (
    WarenkorbID INTEGER PRIMARY KEY,
    BenutzerID INTEGER NOT NULL,
    FOREIGN KEY (BenutzerID) REFERENCES Benutzer(BenutzerID) ON DELETE CASCADE
);

-- OrderItem (schwache Entität)
CREATE TABLE OrderItem (
    OrderItemID INTEGER,
    WarenkorbID INTEGER,
    GerichtID INTEGER,
    Stückzahl INTEGER NOT NULL,
    TotalPrice DECIMAL(8,2),
    RestaurantAnschrift VARCHAR(255),
    PRIMARY KEY (OrderItemID, WarenkorbID),
    FOREIGN KEY (WarenkorbID) REFERENCES Warenkorb(WarenkorbID) ON DELETE CASCADE,
    FOREIGN KEY (GerichtID) REFERENCES Gericht(GerichtID)
);

-- Lieferant 
CREATE TABLE Lieferant (
    LieferantID INTEGER PRIMARY KEY,
    Name VARCHAR(100) NOT NULL,
    Fahrzeug VARCHAR(20) CHECK (Fahrzeug IN ('Auto', 'Fahrrad'))
);

-- Mitglied (für die 1:m-Beziehung zwischen App und PrimeKunde)
CREATE TABLE Mitglied (
    BenutzerID INTEGER PRIMARY KEY,
    AppID INTEGER NOT NULL,
    FOREIGN KEY (BenutzerID) REFERENCES PrimeKunde(BenutzerID) ON DELETE CASCADE,
    FOREIGN KEY (AppID) REFERENCES App(AppID)
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

-- LadetEin (rekursive Beziehung für Benutzer)
CREATE TABLE LadetEin (
    EinladenderID INTEGER,
    EingeladenerID INTEGER,
    PRIMARY KEY (EinladenderID, EingeladenerID),
    FOREIGN KEY (EinladenderID) REFERENCES Benutzer(BenutzerID) ON DELETE CASCADE,
    FOREIGN KEY (EingeladenerID) REFERENCES Benutzer(BenutzerID) ON DELETE CASCADE
);

-- StellEin (für die Beziehung zwischen App und Lieferant)
CREATE TABLE StellEin (
    AppID INTEGER,
    LieferantID INTEGER,
    PRIMARY KEY (AppID, LieferantID),
    FOREIGN KEY (AppID) REFERENCES App(AppID) ON DELETE CASCADE,
    FOREIGN KEY (LieferantID) REFERENCES Lieferant(LieferantID) ON DELETE CASCADE
);

-- Benutzt  (m:1-Beziehung zwischen Benutzer und App)
CREATE TABLE Benutzt (
    BenutzerID INTEGER PRIMARY KEY,
    AppID INTEGER NOT NULL,
    FOREIGN KEY (BenutzerID) REFERENCES Benutzer(BenutzerID) ON DELETE CASCADE,
    FOREIGN KEY (AppID) REFERENCES App(AppID)
);

-- Hat  (Beziehung zwischen Restaurant und App)
CREATE TABLE Hat (
    RestaurantID INTEGER,
    AppID INTEGER,
    PRIMARY KEY (RestaurantID, AppID),
    FOREIGN KEY (RestaurantID) REFERENCES Restaurant(RestaurantID) ON DELETE CASCADE,
    FOREIGN KEY (AppID) REFERENCES App(AppID) ON DELETE CASCADE
);

-- Kocht  (Beziehung zwischen Restaurant und Gericht)
CREATE TABLE Kocht (
    RestaurantID INTEGER,
    GerichtID INTEGER,
    PRIMARY KEY (RestaurantID, GerichtID),
    FOREIGN KEY (RestaurantID) REFERENCES Restaurant(RestaurantID) ON DELETE CASCADE,
    FOREIGN KEY (GerichtID) REFERENCES Gericht(GerichtID) ON DELETE CASCADE
);