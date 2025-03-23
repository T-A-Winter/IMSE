<?php
if(isset($_POST['submitB'])) {
    require_once('DatabaseHelper.php');

//instantiate DatabaseHelper class
    $database = new DatabaseHelper();

//Grab variables from POST request

    $Vorname = '';
    if (isset($_POST['Vorname'])) {
        $Vorname = $_POST['Vorname'];
    }

    $Nachname = '';
    if (isset($_POST['Nachname'])) {
        $Nachname = $_POST['Nachname'];
    }

    $Adresse = '';
    if (isset($_POST['Adresse'])) {
        $Adresse = $_POST['Adresse'];
    }

    $Email = '';
    if (isset($_POST['Email'])) {
        $Email = $_POST['Email'];
    }

    $PromoCode = '';

// Überprüfen, ob ein PromoCode gesetzt und nicht leer ist
    if (!empty($_POST['PromoCode'])) {
        // Speichern des eingegebenen PromoCodes
        $PromoCode = trim($_POST['PromoCode']); // Verwendung von trim() zur Entfernung von Leerzeichen
    } else {
        // Generieren eines zufälligen Promo-Codes, falls kein Code eingegeben wurde
        $PromoCode = 'PROMO' . rand(1000, 9999);
    }


    $Vorwahl = '';
    if (isset($_POST['Vorwahl'])) {
        $Vorwahl = $_POST['Vorwahl'];
    }

    $Telefonnummer = $Vorwahl . (isset($_POST['Telefonnummer']) ? $_POST['Telefonnummer'] : '');

    $Gebuehr = 0.00;
    $GratisLiefern = 0;

// Check if the PrimeKunde button was clicked
    if (isset($_POST['becomePrime'])) {
        $Gebuehr = 15.00; // Set fee to 15 Euros
        $GratisLiefern = 1; // Enable free delivery
    }

// Insert method
    $success = $database->insertIntoBenutzer($Vorname, $Nachname, $Adresse, $Email, $PromoCode, $Telefonnummer, $Gebuehr, $GratisLiefern);

// Check result
    if ($success) {
        echo "Benuzter '{$Vorname} {$Nachname}' successfully added!'";
    } else {
        echo "Error can't insert Person '{$Vorname} {$Nachname}'!";
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Add Benutzer</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #FF8000;
            margin: 0;
            padding: 20px;
        }
        .container {
            width: 80%;
            margin: 20px auto;
            background: white;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        h2, label {
            color: #333;
        }
        input, select, button {
            width: 100%;
            padding: 8px;
            margin: 5px 0 20px 0;
            display: inline-block;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-sizing: border-box;
        }
        button {
            width: auto;
            background-color: #ff6900;
            color: white;
            padding: 14px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #ff6900;
        }
        .back-link {
            color: #ff6900;
            text-decoration: none;
        }
        .back-link:hover {
            text-decoration: underline;
        }

        .logo {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
        }

        .logo img {
            width: 100px;
            height: auto;
        }


    </style>
</head>
<body>
<div class="logo">
    <a href="index.php" class="logo">
    <img src="Logo.png" alt="Ayran Food Delivery Logo">
</div>

<div class="container">
<a href="index.php" class="back-link">&laquo; Zurück</a>
    <h2>Add Benutzer:</h2>
    <form method="post" action="addPerson.php">
        <div>
            <label for="new_Vorname">Vorname:</label>
            <input id="new_Vorname" name="Vorname" type="text" maxlength="20">
        </div>

        <div>
            <label for="new_Nachname">Nachname:</label>
            <input id="new_Nachname" name="Nachname" type="text" maxlength="20">
        </div>

        <div>
            <label for="new_Adresse">Adresse:</label>
            <input id="new_Adresse" name="Adresse" type="text" maxlength="50">
        </div>

        <div>
            <label for="new_Email">Email:</label>
            <input id="new_Email" name="Email" type="text" maxlength="20">
        </div>

        <div>
            <label for="new_Vorwahl">Vorwahl:</label>
            <select id="new_Vorwahl" name="Vorwahl">
                <option value="+43">+43 Österreich</option>
                <option value="+49">+49 Deutschland</option>
                <option value="+41">+41 Schweiz</option>
            </select>
        </div>

        <div>
            <label for="new_Telefonnummer">Telefonnummer:</label>
            <input id="new_Telefonnummer" name="Telefonnummer" type="text" maxlength="15">
        </div>

        <div>
            <label for="new_PromoCode">PromoCode:</label>
            <input id="new_PromoCode" name="PromoCode" type="text" maxlength="20" placeholder="Optional">
        </div>

        <div>
        <label for="primeCustomer">PrimeKunde werden (15€ Gebühr):</label>
        <input type="checkbox" id="primeCustomer" name="becomePrime" onchange="handlePrimeChange()">
        </div>

        <div>
            <button  name="submitB" type="submit">Add Benutzer</button>
        </div>
    </form>
</div>
</body>
</html>