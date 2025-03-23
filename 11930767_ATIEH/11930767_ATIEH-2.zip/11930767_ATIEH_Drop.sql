DROP TABLE App;
DROP TABLE Benutzer;
DROP TABLE Restaurant;
DROP TABLE Gericht;
DROP TABLE Lieferrant;
DROP TABLE Warenkorb;
DROP TABLE OrderItem;
DROP TABLE Kochen;

DROP SEQUENCE BenutzerIDSeq;
DROP SEQUENCE GerichtIDSeq;
DROP SEQUENCE LieferrantIDSeq;
DROP SEQUENCE WarenkorbIDSeq;
DROP SEQUENCE OrderItemIDSeq;

DROP TRIGGER CheckEmailBeforeInsert;
DROP TRIGGER BenutzerBeforeInsert;
DROP TRIGGER GerichtBeforeInsert;
DROP TRIGGER LieferrantBeforeInsert;
DROP TRIGGER WarenkorbBeforeInsert;
DROP TRIGGER OrderItemBeforeInsert;
DROP TRIGGER WarenkorbBeforeInsert;

DROP PROCEDURE p_delete_Benutzer;
DROP PROCEDURE p_delete_Restaurant;
DROP PROCEDURE p_delete_Gericht;
DROP PROCEDURE p_delete_Lieferrant;
DROP PROCEDURE p_delete_Warenkorb;
DROP PROCEDURE p_delete_OrderItem;
DROP PROCEDURE p_avg_price_of_restaurant;
