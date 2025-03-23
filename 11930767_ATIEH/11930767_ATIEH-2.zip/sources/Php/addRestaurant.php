<?php
if(isset($_POST['submitR'])) {
    require_once('DatabaseHelper.php');

    $database = new DatabaseHelper();

//Grab variables from POST request


    $RestaurantName = '';
    if (isset($_POST['RestaurantName'])) {
        $RestaurantName = $_POST['RestaurantName'];
    }

    $Anschrift = '';
    if (isset($_POST['Anschrift'])) {
        $Anschrift = $_POST['Anschrift'];
    }

    $Oeffnungszeiten = '';
// Überprüfen, ob ein PromoCode gesetzt und nicht leer ist
    if (!empty($_POST['Oeffnungszeiten'])) {
        // Speichern des eingegebenen PromoCodes
        $Oeffnungszeiten = trim($_POST['Oeffnungszeiten']); // Verwendung von trim() zur Entfernung von Leerzeichen
    } else {
        // Generieren eines zufälligen Promo-Codes, falls kein Code eingegeben wurde
        $Oeffnungszeiten = "10:00";
    }

    $Ort = '';
    if (isset($_POST['Ort'])) {
        $Ort = $_POST['Ort'];
    }

    $Plz = '';
    if (isset($_POST['Plz'])) {
        $Plz = $_POST['Plz'];
    }

// Insert method
    $success = $database->insertIntoRestaurant($RestaurantName, $Anschrift, $Oeffnungszeiten, $Ort, $Plz);

// Check result
    if ($success) {
        echo "Restaurant '{$RestaurantName} {$Anschrift}' successfully added!'";
    } else {
        echo "Error can't insert Person '{$RestaurantName} {$Anschrift}'!";
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Add Restaurant</title>
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
        input, button {
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
<div class="container">
    <a href="index.php" class="logo">
        <img src="Logo.png" alt="Ayran Food Delivery Logo">
    </a>

    <a href="index.php" class="back-link">&laquo; Zurück</a>
    <h2>Add Restaurant:</h2>
    <form method="post" action="addRestaurant.php">
        <div>
            <label for="new_RestaurantName">RestaurantName:</label>
            <input id="new_RestaurantName" name="RestaurantName" type="text" maxlength="20">
        </div>
        <div>
            <label for="new_Anschrift">Anschrift:</label>
            <input id="new_Anschrift" name="Anschrift" type="text" maxlength="20">
        </div>
        <div>
            <label for="new_Oeffnungszeiten">Oeffnungszeiten:</label>
            <input id="new_Oeffnungszeiten" name="Oeffnungszeiten" type="text" maxlength="5">
        </div>
        <div>
            <label for="new_Ort">Ort:</label>
            <input id="new_Ort" name="Ort" type="text" maxlength="20">
        </div>
        <div>
            <label for="new_Plz">Plz:</label>
            <input id="new_Plz" name="Plz" type="text" maxlength="20">
        </div>
        <div>
            <button name="submitR" type="submit">Add Restaurant</button>
        </div>
    </form>
</div>
</body>
</html>
