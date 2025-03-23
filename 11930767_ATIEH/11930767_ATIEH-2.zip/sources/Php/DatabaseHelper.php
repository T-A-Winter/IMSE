<?php

class DatabaseHelper
{
    const username = 'a11930767';
    const password = 'dbs23';
    const con_string = '//oracle19.cs.univie.ac.at:1521/orclcdb';
    protected $conn;

    public function __construct()
    {
        try {
            $this->conn = oci_connect(
                DatabaseHelper::username,
                DatabaseHelper::password,
                DatabaseHelper::con_string
            );

            if (!$this->conn) {
                die("DB error: Connection can't be established!");
            }

        } catch (Exception $e) {
            die("DB error: {$e->getMessage()}");
        }
    }

    public function __destruct()
    {
        // clean up
        oci_close($this->conn);
    }


    //DatabaseHelper Benutzer !
    public function selectBenutzer($BenutzerID, $Vorname, $Nachname, $Adresse, $Email, $PromoCode, $Telefonnummer, $premiumFilter)
    {
        $sql = "SELECT * FROM Benutzer WHERE 1=1";
        if (!empty($BenutzerID)) {
            $sql .= " AND BenutzerID = :BenutzerID";
        }

        // Append to the SQL statement for each parameter if provided
        if (!empty($Vorname)) {
            $sql .= " AND upper(Vorname) LIKE upper(:Vorname)";
        }
        if (!empty($Nachname)) {
            $sql .= " AND upper(Nachname) LIKE upper(:Nachname)";
        }
        if (!empty($Adresse)) {
            $sql .= " AND upper(Adresse) LIKE upper(:Adresse)";
        }
        if (!empty($Email)) {
            $sql .= " AND upper(Email) LIKE upper(:Email)";
        }
        if (!empty($PromoCode)) {
            $sql .= " AND upper(PromoCode) LIKE upper(:PromoCode)";
        }
        if (!empty($Telefonnummer)) {
            $sql .= " AND upper(Telefonnummer) LIKE upper(:Telefonnummer)";
        }

        if ($premiumFilter === true) {
            $sql .= " AND GratisLiefern = 1";
        }

        $sql .= " ORDER BY BENUTZERID ASC";

        $statement = oci_parse($this->conn, $sql);

        // Bind the parameters if they are not empty
        if (!empty($BenutzerID)) {
            oci_bind_by_name($statement, ':BenutzerID', $BenutzerID);
        }
        if (!empty($Vorname)) {
            $Vorname = "%$Vorname%";
            oci_bind_by_name($statement, ':Vorname', $Vorname);
        }
        if (!empty($Nachname)) {
            $Nachname = "%$Nachname%";
            oci_bind_by_name($statement, ':Nachname', $Nachname);
        }
        if (!empty($Adresse)) {
            $Adresse = "%$Adresse%";
            oci_bind_by_name($statement, ':Adresse', $Adresse);
        }
        if (!empty($Email)) {
            $Email = "%$Email%";
            oci_bind_by_name($statement, ':Email', $Email);
        }
        if (!empty($PromoCode)) {
            $PromoCode = "%$PromoCode%";
            oci_bind_by_name($statement, ':PromoCode', $PromoCode);
        }
        if (!empty($Telefonnummer)) {
            $Telefonnummer = "%$Telefonnummer%";
            oci_bind_by_name($statement, ':Telefonnummer', $Telefonnummer);
        }


        oci_execute($statement);
        oci_fetch_all($statement, $res, 0, -1, OCI_FETCHSTATEMENT_BY_ROW);
        oci_free_statement($statement);
        return $res;
    }

    public function insertIntoBenutzer($Vorname, $Nachname, $Adresse, $Email, $PromoCode, $Telefonnummer, $Gebuehr, $GratisLiefern)
    {
        if (empty($PromoCode)) {
            $PromoCode = 'PROMO' . rand(1000, 9999);
        }
        $sql = "INSERT INTO Benutzer (Vorname, Nachname, Adresse, Email, PromoCode, Telefonnummer, Gebuehr, GratisLiefern) 
            VALUES (:vorname, :nachname, :adresse, :email, :promocode, :telefonnummer, :gebuehr, :gratisliefern)";

        $statement = oci_parse($this->conn, $sql);

        // Bind Variables to the statement
        oci_bind_by_name($statement, ':vorname', $Vorname);
        oci_bind_by_name($statement, ':nachname', $Nachname);
        oci_bind_by_name($statement, ':adresse', $Adresse);
        oci_bind_by_name($statement, ':email', $Email);
        oci_bind_by_name($statement, ':promocode', $PromoCode);
        oci_bind_by_name($statement, ':telefonnummer', $Telefonnummer);
        oci_bind_by_name($statement, ':gebuehr', $Gebuehr);
        oci_bind_by_name($statement, ':gratisliefern', $GratisLiefern);

        // Execute the statement and handle errors
        $success = oci_execute($statement);
        if (!$success) {
            $e = oci_error($statement);
            error_log("Error in insertIntoBenutzer: " . $e['message']); // Log the error
            oci_rollback($this->conn); // Rollback the transaction if error
            oci_free_statement($statement);
            return false;
        }

        oci_commit($this->conn);
        oci_free_statement($statement);

        return true;
    }


    public function deleteBenutzer($BenutzerID)
    {
        $errorcode = 0;
        $sql = 'BEGIN P_DELETE_BENUTZER(:BenutzerID, :errorcode); END;';
        $statement = oci_parse($this->conn, $sql);
        oci_bind_by_name($statement, ':BenutzerID', $BenutzerID);
        oci_bind_by_name($statement, ':errorcode', $errorcode);
        try {
            oci_execute($statement);
        } catch (Exception $e) {
            error_log("Fehler beim Ausführen der Stored Procedure: " . $e->getMessage());
            return -1; // oder ein anderer Fehlercode
        }
        oci_free_statement($statement);
        return $errorcode;
    }

    //DatabaseHelper Restaurant !

    public function getRestaurantAddressesA() {
        $addresses = array();
        $query = "SELECT Anschrift FROM Restaurant";
        $result = oci_parse($this->conn, $query);
        oci_execute($result);
        while ($row = oci_fetch_assoc($result)) {
            $addresses[] = $row['ANSCHRIFT'];
        }
        return $addresses;
    }

    public function getAveragePrice($restaurantAnschrift) {
        $avgPrice = null; // Declare the variable before using it

        try {
            $stmt = oci_parse($this->conn, "BEGIN P_AVG_PRICE_OF_RESTAURANT(:p_RestaurantAnschrift, :p_avg_price); END;");
            oci_bind_by_name($stmt, ':p_RestaurantAnschrift', $restaurantAnschrift, -1, SQLT_CHR);
            oci_bind_by_name($stmt, ':p_avg_price', $avgPrice, -1, SQLT_INT);

            oci_execute($stmt);

            // Return the average price
            return $avgPrice;
        } catch (Exception $e) {
            echo "Error: " . $e->getMessage();
            return -1; // Return an error flag if an exception occurs
        }
    }

    public function updateRestaurant($Anschrift, $newName = null, $newOeffnungszeiten = null) {
        $sql = "UPDATE Restaurant SET ";
        $params = array();

        if ($newName !== null) {
            $sql .= "RestaurantName = :newName";
            $params[':newName'] = $newName;
        }

        if ($newOeffnungszeiten !== null) {
            if ($newName !== null) {
                $sql .= ", ";
            }
            $sql .= "Oeffnungszeiten = :newOeffnungszeiten";
            $params[':newOeffnungszeiten'] = $newOeffnungszeiten;
        }

        $sql .= " WHERE Anschrift = :Anschrift";
        $params[':Anschrift'] = $Anschrift;

        $statement = oci_parse($this->conn, $sql);

        foreach ($params as $key => &$val) {
            oci_bind_by_name($statement, $key, $val);
        }

        $result = oci_execute($statement);
        oci_free_statement($statement);

        return $result;
    }

    public function selectAllRestaurant($RestaurantName, $Anschrift, $Oeffnungszeiten, $Ort, $Plz)
    {
        $sql = "SELECT * FROM Restaurant
                WHERE Anschrift LIKE '%{$Anschrift}%'
                  AND upper(RestaurantName) LIKE upper('%{$RestaurantName}%')
                  AND upper(Oeffnungszeiten) LIKE upper('%{$Oeffnungszeiten}%')
                  AND upper(Ort) LIKE upper('%{$Ort}%')
                  AND upper(Plz) LIKE upper('%{$Plz}%')
                ORDER BY RESTAURANTNAME ASC"; // Stellen Sie sicher, dass 'NAME' der korrekte Feldname ist

        $statement = oci_parse($this->conn, $sql);
        oci_execute($statement);
        oci_fetch_all($statement, $res, 0, -1, OCI_FETCHSTATEMENT_BY_ROW);
        oci_free_statement($statement);
        return $res;
    }
    public function selectRestaurant($RestaurantName, $Anschrift, $Oeffnungszeiten, $Ort, $Plz)
    {
        // Start with the base SQL statement
        $sql = "SELECT * FROM Restaurant WHERE 1=1";

        if (!empty($RestaurantName)) {
            $sql .= " AND upper(RestaurantName) LIKE upper(:RestaurantName)";
        }
        if (!empty($Anschrift)) {
            $sql .= " AND Anschrift = :Anschrift";
        }
        if (!empty($Oeffnungszeiten)) {
            $sql .= " AND upper(Oeffnungszeiten) LIKE upper(:Oeffnungszeiten)";
        }
        if (!empty($Ort)) {
            $sql .= " AND upper(Ort) LIKE upper(:Ort)";
        }
        if (!empty($Plz)) {
            $sql .= " AND upper(Plz) LIKE upper(:Plz)";
        }

        $sql .= " ORDER BY RESTAURANTNAME ASC";

        $statement = oci_parse($this->conn, $sql);

        // Bind parameters
        if (!empty($RestaurantName)) {
            $RestaurantName = "%$RestaurantName%";
            oci_bind_by_name($statement, ':RestaurantName', $RestaurantName);
        }
        if (!empty($Anschrift)) {
            oci_bind_by_name($statement, ':Anschrift', $Anschrift);
        }
        if (!empty($Oeffnungszeiten)) {
            $Oeffnungszeiten = "%$Oeffnungszeiten%";
            oci_bind_by_name($statement, ':Oeffnungszeiten', $Oeffnungszeiten);
        }
        if (!empty($Ort)) {
            $Ort = "%$Ort%";
            oci_bind_by_name($statement, ':Ort', $Ort);
        }
        if (!empty($Plz)) {
            $Plz = "%$Plz%";
            oci_bind_by_name($statement, ':Plz', $Plz);
        }

        oci_execute($statement);
        oci_fetch_all($statement, $res, 0, -1, OCI_FETCHSTATEMENT_BY_ROW);
        oci_free_statement($statement);
        return $res;
    }


    public function insertIntoRestaurant($RestaurantName, $Anschrift, $Oeffnungszeiten, $Ort, $Plz)
    {
        if (empty($_POST['Oeffnungszeiten'])) {
            $Oeffnungszeiten = "10:00";
        }
        $sql = "INSERT INTO Restaurant (RestaurantName, Anschrift, Oeffnungszeiten, Ort, Plz) 
                VALUES ('{$RestaurantName}', '{$Anschrift}', '{$Oeffnungszeiten}', '{$Ort}', '{$Plz}')";

        $statement = oci_parse($this->conn, $sql);
        $success = oci_execute($statement) && oci_commit($this->conn);
        oci_free_statement($statement);
        return $success;
    }

    public function deleteRestaurant($Anschrift)
    {
        $errorcode = 0;
        $sql = 'BEGIN P_DELETE_RESTAURANT(:Anschrift, :errorcode); END;';
        $statement = oci_parse($this->conn, $sql);
        oci_bind_by_name($statement, ':Anschrift', $Anschrift, -1, SQLT_CHR);
        oci_bind_by_name($statement, ':errorcode', $errorcode, -1, OCI_B_INT);
        if (!oci_execute($statement)) {
            $e = oci_error($statement);
            echo "Fehler beim Ausführen der Prozedur: " . $e['message'];
        }
        oci_free_statement($statement);
        return $errorcode;
    }

// DatabaseHelper Gericht !


    public function updateGericht($GerichtID, $newName, $newPrice) {
        $sql = "UPDATE Gericht SET GerichtName = :newName, Price = :newPrice WHERE GerichtID = :GerichtID";

        $statement = oci_parse($this->conn, $sql);
        oci_bind_by_name($statement, ':newName', $newName);
        oci_bind_by_name($statement, ':newPrice', $newPrice);
        oci_bind_by_name($statement, ':GerichtID', $GerichtID);

        $result = oci_execute($statement);
        oci_free_statement($statement);

        return $result;
    }

    public function selectGericht($GerichtID, $RestaurantAnschrift, $GerichtName, $Price)
    {
        // Start with the base SQL statement
        $sql = "SELECT * FROM Gericht WHERE 1=1";

        if (!empty($GerichtName)) {
            $sql .= " AND GerichtName LIKE :GerichtName";
        }
        if (!empty($GerichtID)) {
            $sql .= " AND GerichtID = :GerichtID";
        }
        if (!empty($RestaurantAnschrift)) {
            $sql .= " AND upper(RestaurantAnschrift) LIKE upper(:RestaurantAnschrift)";
        }
        if (!empty($Price)) {
            $sql .= " AND Price = :Price";
        }

        $sql .= " ORDER BY RestaurantAnschrift ASC";

        $statement = oci_parse($this->conn, $sql);

        if (!empty($GerichtName)) {
            $GerichtName = "%$GerichtName%";
            oci_bind_by_name($statement, ':GerichtName', $GerichtName);
        }
        if (!empty($GerichtID)) {
            oci_bind_by_name($statement, ':GerichtID', $GerichtID);
        }
        if (!empty($RestaurantAnschrift)) {
            $RestaurantAnschrift = "$RestaurantAnschrift";
            oci_bind_by_name($statement, ':RestaurantAnschrift', $RestaurantAnschrift);
        }
        if (!empty($Price)) {
            oci_bind_by_name($statement, ':Price', $Price);
        }

        oci_execute($statement);
        oci_fetch_all($statement, $res, 0, -1, OCI_FETCHSTATEMENT_BY_ROW);
        oci_free_statement($statement);
        return $res;
    }


    public function selectGerichteByAnschrift($RestaurantAnschrift) {
        $gerichteArray = array();
        $sql = "SELECT GERICHTID, RESTAURANTANSCHRIFT, GERICHTNAME, PRICE FROM Gericht WHERE RestaurantAnschrift = :Anschrift"; // Make sure you have a PRICE column in your Gericht table
        $stmt = oci_parse($this->conn, $sql);
        oci_bind_by_name($stmt, ':Anschrift', $RestaurantAnschrift);
        oci_execute($stmt);
        if ($e = oci_error($stmt)) {
            var_dump($e);
        }

        while ($row = oci_fetch_assoc($stmt)) {
            array_push($gerichteArray, $row);
        }

        oci_free_statement($stmt);
        return $gerichteArray;
    }

    public function getRestaurantAddresses() {
        $sql = "SELECT Anschrift FROM Restaurant";
        $result = oci_parse($this->conn, $sql);
        oci_execute($result);
        return $result;
    }

    public function insertIntoGericht($GerichtID, $RestaurantAnschrift, $GerichtName, $Price)
    {
        $sql = "INSERT INTO Gericht (GerichtID, RestaurantAnschrift, GerichtName, Price) 
            VALUES (:GerichtID, :RestaurantAnschrift, :GerichtName, :Price)";

        $statement = oci_parse($this->conn, $sql);

        oci_bind_by_name($statement, ':GerichtID', $GerichtID);
        oci_bind_by_name($statement, ':RestaurantAnschrift', $RestaurantAnschrift);
        oci_bind_by_name($statement, ':GerichtName', $GerichtName);
        oci_bind_by_name($statement, ':Price', $Price);

        $success = oci_execute($statement, OCI_NO_AUTO_COMMIT); // Verwenden Sie OCI_NO_AUTO_COMMIT für Transaktionen
        if ($success) {
            oci_commit($this->conn);
        } else {
            oci_rollback($this->conn);
        }
        oci_free_statement($statement);
        return $success;
    }

    public function deleteGericht($GerichtID)
    {
        // Ein ungültiger Standardwert für den Fehlercode, um nicht erkannte Fehler zu identifizieren
        $errorcode = -1;
        $sql = 'BEGIN P_DELETE_GERICHT(:GerichtID, :errorcode); END;';
        $statement = oci_parse($this->conn, $sql);

        oci_bind_by_name($statement, ':GerichtID', $GerichtID);
        oci_bind_by_name($statement, ':errorcode', $errorcode, -1, OCI_B_INT);

        if (!oci_execute($statement)) {
            $e = oci_error($statement);
            echo "Fehler beim Ausführen der Prozedur: " . $e['message'];
        }

        oci_free_statement($statement);
        return $errorcode;
    }

    public function isPrimeKunde($BenutzerID) {
        $sql = "SELECT GratisLiefern FROM Benutzer WHERE BenutzerID = :BenutzerID";
        $stmt = oci_parse($this->conn, $sql);
        oci_bind_by_name($stmt, ':BenutzerID', $BenutzerID);
        oci_execute($stmt);
        $row = oci_fetch_assoc($stmt);
        oci_free_statement($stmt);
        return $row && $row['GRATISLIEFERN'] == 1;
    }

    public function getGericht($GerichtID) {
        $sql = "SELECT Price, RestaurantAnschrift FROM Gericht WHERE GerichtID = :GerichtID";
        $stmt = oci_parse($this->conn, $sql);
        oci_bind_by_name($stmt, ':GerichtID', $GerichtID);
        oci_execute($stmt);
        $row = oci_fetch_assoc($stmt);
        oci_free_statement($stmt);

        return $row;
    }

    public function insertWarenkorb($userID, $items) {
        $isPrime = $this->isPrimeKunde($userID);
        $liefernKosten = $isPrime ? 0 : 3;

        $firstItem = reset($items);
        $gericht = $this->getGericht($firstItem['GerichtID']);
        $restaurantAnschrift = $gericht['RESTAURANTANSCHRIFT'];

        // Insert into Warenkorb table (one order)
        $sql = "INSERT INTO Warenkorb (BenutzerID, ResturantAnschrift, LiefernKosten) VALUES (:benutzerID, :resturantAnschrift, :liefernKosten) RETURNING WarenkorbID INTO :warenkorbID";

        $statement = oci_parse($this->conn, $sql);
        oci_bind_by_name($statement, ':benutzerID', $userID);
        oci_bind_by_name($statement, ':resturantAnschrift', $restaurantAnschrift);
        oci_bind_by_name($statement, ':liefernKosten', $liefernKosten);
        oci_bind_by_name($statement, ':warenkorbID', $warenkorbID, -1, SQLT_INT); // Bind the WarenkorbID variable

        // Execute and fetch the new WarenkorbID
        if (!oci_execute($statement)) {
            $e = oci_error($statement);
            echo "Fehler beim Einfügen ins Warenkorb: " . $e['message'];
            return false; // Return false if order insertion fails
        }

        $newWarenkorbID = $warenkorbID;
        oci_free_statement($statement);

        // Insert into OrderItem table (multiple items for one order)
        foreach ($items as $item) {
            $gerichtID = $item['GerichtID'];
            $quantity = $item['Quantity'];
            $gericht = $this->getGericht($item['GerichtID']);
            $price = $gericht['PRICE'];
            $totalPriceG = $quantity * $price;

            $sqlItem = "INSERT INTO OrderItem (WarenkorbID, GerichtID, Price, Quantity, TotalPriceG) VALUES (:warenkorbID, :gerichtID, :price, :quantity, :totalPriceG)";
            $statementItem = oci_parse($this->conn, $sqlItem);

            oci_bind_by_name($statementItem, ':warenkorbID', $newWarenkorbID);
            oci_bind_by_name($statementItem, ':gerichtID', $gerichtID);
            oci_bind_by_name($statementItem, ':price', $price);
            oci_bind_by_name($statementItem, ':quantity', $quantity);
            oci_bind_by_name($statementItem, ':totalPriceG', $totalPriceG);

            if (!oci_execute($statementItem)) {
                $e = oci_error($statementItem);
                echo "Fehler beim Einfügen ins OrderItem: " . $e['message'];
                oci_free_statement($statementItem);
                return false; // Return false if any item insertion fails
            }
            oci_free_statement($statementItem);
        }

        return true; // Return true if everything was successful
    }


    // DatabaseHelper Lieferrant !


    public function selectLieferrant($LieferrantID = null, $LieferrantName = null, $FahrzeugTyp = null)
    {
        // Basissql-Statement für alle Lieferranten
        $sql = "SELECT * FROM Lieferrant ORDER BY LIEFERRANTID ASC";

        // Falls Suchparameter angegeben sind, fügen Sie WHERE-Bedingungen hinzu
        $conditions = array();
        if ($LieferrantID) {
            $conditions[] = "LieferrantID LIKE upper('(%{$LieferrantID}%)')";
        }
        if ($LieferrantName) {
            $conditions[] = "upper(LieferrantName) LIKE upper('%{$LieferrantName}%')";
        }
        if ($FahrzeugTyp) {
            $conditions[] = "upper(FahrzeugTyp) LIKE upper('%{$FahrzeugTyp}%')";
        }
        if (count($conditions) > 0) {
            // Fügen Sie die WHERE-Bedingungen zum SQL-Statement hinzu
            $sql = "SELECT * FROM Lieferrant WHERE " . implode(' AND ', $conditions) . " ORDER BY LIEFERRANTID ASC";
        }

        $statement = oci_parse($this->conn, $sql);
        oci_execute($statement);
        oci_fetch_all($statement, $res, 0, -1, OCI_FETCHSTATEMENT_BY_ROW);
        oci_free_statement($statement);
        return $res;
    }


    public function insertIntoLieferrant($LieferrantName, $FahrzeugTyp)
    {
        $sql = "INSERT INTO Lieferrant (LieferrantName, FahrzeugTyp) 
                VALUES ('{$LieferrantName}', '{$FahrzeugTyp}')";

        $statement = oci_parse($this->conn, $sql);
        $success = oci_execute($statement);
        if (!$success) {
            $e = oci_error($statement);
            echo "Fehler bei der Datenbankoperation: " . $e['message'];
        }
        oci_commit($this->conn);
        oci_free_statement($statement);
        return $success;
    }

    public function deleteLieferrant($LieferrantID)
    {
        $errorcode = 0;
        $sql = 'BEGIN P_DELETE_LIEFERRANT(:LieferrantID, :errorcode); END;';
        $statement = oci_parse($this->conn, $sql);
        oci_bind_by_name($statement, ':LieferrantID', $LieferrantID);
        oci_bind_by_name($statement, ':errorcode', $errorcode);
        try {
            oci_execute($statement);
        } catch (Exception $e) {
            error_log("Fehler beim Ausführen der Stored Procedure: " . $e->getMessage());
            return -1; // oder ein anderer Fehlercode
        }
        return $errorcode;
    }

    // DatabaseHelper Warenkorb !

    public function selectAllWarenkorb($WarenkorbID, $BenutzerID, $ResturantAnschrift, $LiefernKosten)
    {
        $sql = "SELECT * FROM Warenkorb WHERE WarenkorbID LIKE ('%{$WarenkorbID}%')
                  AND upper(BenutzerID) LIKE upper('%{$BenutzerID}%')
                  AND upper(ResturantAnschrift) LIKE upper('%{$ResturantAnschrift}%')
                  AND upper(LiefernKosten) LIKE upper('%{$LiefernKosten}%')
                ORDER BY WARENKORBID ASC"; // Stellen Sie sicher, dass 'NAME' der korrekte Feldname ist

        $statement = oci_parse($this->conn, $sql);
        oci_execute($statement);
        oci_fetch_all($statement, $res, 0, -1, OCI_FETCHSTATEMENT_BY_ROW);
        oci_free_statement($statement);

        return $res;
    }
    public function selectWarenkorb($WarenkorbID, $BenutzerID, $ResturantAnschrift, $LiefernKosten)
    {
        $sql = "SELECT * FROM Warenkorb WHERE 1=1";

        if ($WarenkorbID !== '') {
            $sql .= " AND WarenkorbID = :WarenkorbID";
        }

        if ($BenutzerID !== '') {
            $sql .= " AND upper(BenutzerID) LIKE upper(:BenutzerID)";
        }

        if ($ResturantAnschrift !== '') {
            $sql .= " AND upper(ResturantAnschrift) LIKE upper(:ResturantAnschrift)";
        }

        if ($LiefernKosten !== '') {
            $sql .= " AND upper(LiefernKosten) LIKE upper(:LiefernKosten)";
        }

        $sql .= " ORDER BY WARENKORBID ASC";

        $statement = oci_parse($this->conn, $sql);

        // Bind the parameters if they are not empty
        if ($WarenkorbID !== '') {
            oci_bind_by_name($statement, ':WarenkorbID', $WarenkorbID);
        }

        if ($BenutzerID !== '') {
            oci_bind_by_name($statement, ':BenutzerID', $BenutzerID);
        }

        if ($ResturantAnschrift !== '') {
            oci_bind_by_name($statement, ':ResturantAnschrift', $ResturantAnschrift);
        }

        if ($LiefernKosten !== '') {
            oci_bind_by_name($statement, ':LiefernKosten', $LiefernKosten);
        }

        oci_execute($statement);
        oci_fetch_all($statement, $res, 0, -1, OCI_FETCHSTATEMENT_BY_ROW);
        oci_free_statement($statement);

        return $res;
    }

    // DatabaseHelper OrderItem !


    public function selectAllOrderItem($WarenkorbID, $OrderItemID, $GerichtID, $Price, $Quantity, $TotalPriceG)
    {
        // Define the sql statement string
        $sql = "SELECT * FROM OrderItem WHERE OrderItemID LIKE ('%{$OrderItemID}%')
                  AND upper(WarenkorbID) LIKE upper('%{$WarenkorbID}%')
                  AND upper(GerichtID) LIKE upper('%{$GerichtID}%')
                  AND upper(Price) LIKE upper('%{$Price}%')
                          AND upper(Quantity) LIKE upper('%{$Quantity}%')
                        AND upper(TotalPriceG) LIKE upper('%{$TotalPriceG}%')
                ORDER BY ORDERITEMID ASC"; // Stellen Sie sicher, dass 'NAME' der korrekte Feldname ist

        $statement = oci_parse($this->conn, $sql);

        oci_execute($statement);
        oci_fetch_all($statement, $res, 0, -1, OCI_FETCHSTATEMENT_BY_ROW);

        oci_free_statement($statement);

        return $res;
    }

    public function selectOrderItem($WarenkorbID, $OrderItemID, $GerichtID, $Price, $Quantity, $TotalPriceG)
    {
        $sql = "SELECT * FROM OrderItem WHERE 1=1";

        if ($WarenkorbID !== '') {
            $sql .= " AND upper(WarenkorbID) LIKE upper('%{$WarenkorbID}%')";
        }

        if ($OrderItemID !== '') {
            $sql .= " AND OrderItemID = '{$OrderItemID}'";
        }

        if ($GerichtID !== '') {
            $sql .= " AND upper(GerichtID) LIKE upper('%{$GerichtID}%')";
        }
        $sql .= " ORDER BY ORDERITEMID ASC";

        $statement = oci_parse($this->conn, $sql);
        oci_execute($statement);
        oci_fetch_all($statement, $res, 0, -1, OCI_FETCHSTATEMENT_BY_ROW);
        oci_free_statement($statement);

        return $res;
    }

}