<?php

ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);
require_once('DatabaseHelper.php');
$database = new DatabaseHelper();
$BenutzerID = '';
if (isset($_GET['BenutzerID'])) {
    $BenutzerID = $_GET['BenutzerID'];
}

$Vorname = '';
if (isset($_GET['Vorname'])) {
    $Vorname = $_GET['Vorname'];
}

$Nachname = '';
if (isset($_GET['Nachname'])) {
    $Nachname = $_GET['Nachname'];
}

$Adresse = '';
if (isset($_GET['Adresse'])) {
    $Adresse = $_GET['Adresse'];
}

$Email = '';
if (isset($_GET['Email'])) {
    $Email = $_GET['Email'];
}

$PromoCode = '';
if (isset($_GET['PromoCode'])) {
    $PromoCode = $_GET['PromoCode'];
}

$Telefonnummer = '';
if (isset($_GET['Telefonnummer'])) {
    $Telefonnummer = $_GET['Telefonnummer'];
}

$premiumFilter = '';
if (isset($_GET['filter_premium']) && $_GET['filter_premium'] == 'on') {
    $premiumFilter = true; // Or however you represent premium status in your database
} else {
    $premiumFilter = false;
}

$person_array = $database->selectBenutzer($BenutzerID, $Vorname, $Nachname, $Adresse, $Email, $PromoCode, $Telefonnummer, $premiumFilter);
?>


<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Search Benutzer</title>
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
        h1, h2, label, th, td {
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
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        tr:nth-child(even){background-color: #f2f2f2;}
        th {
            padding-top: 12px;
            padding-bottom: 12px;
            background-color: #ff6900;
            color: white;
        }
        .back-link {
            color: #ff6900;
            text-decoration: none;
        }
        .back-link:hover {
            text-decoration: underline;
        }
        .scrollable-table {
            overflow-x: auto; /* Scroll horizontally if needed */
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
    </a>
</div>
<div class="container">
    <a href="index.php" class="back-link">&laquo; Zurück</a>
    <h1>Search Benutzer</h1>

    <!-- Search form Benutzer -->
    <h2>Benutzer Search:</h2>
    <form method="get">
        <div>
            <label for="BenutzerID">BenutzerID:</label>
            <input id="BenutzerID" name="BenutzerID" type="text" value='<?php echo $BenutzerID; ?>' min="0">
        </div>
        <div>
            <label for="Vorname">Vorname:</label>
            <input id="Vorname" name="Vorname" type="text" value='<?php echo $Vorname; ?>' min="0">
        </div>
        <div>
            <label for="Adresse">Nachname:</label>
            <input id="Nachname" name="Nachname" type="text" value='<?php echo $Nachname; ?>' min="0">
        </div>
        <div>
            <label for="Adresse">Adresse:</label>
            <input id="Adresse" name="Adresse" type="text" value='<?php echo $Adresse; ?>' min="0">
        </div>
        <div>
            <label for="Email">Email:</label>
            <input id="Email" name="Email" type="text" value='<?php echo $Email; ?>' min="0">
        </div>
        <div class="form-group">
            <label for="filter_premium">Kunden mit Premiummitgliedschaft anzeigen:</label>
            <input id="filter_premium" name="filter_premium" type="checkbox" <?php echo (isset($_GET['filter_premium']) && $_GET['filter_premium'] == 'on') ? 'checked' : ''; ?>>
        </div>

        <div>
            <button id='submit' type='submit'>Search</button>
        </div>
    </form>
    <br>
    <hr>

    <!-- Search result -->
    <div class="scrollable-table">
    <h2>Benuzter Search Result:</h2>
    <table>
        <tr>
            <th>BenuzterID</th>
            <th>Vorname</th>
            <th>Nachname</th>
            <th>Adresse</th>
            <th>Email</th>
            <th>PromoCode</th>
            <th>Telefonnummer</th>
            <th>Gebuehr</th>
            <th>Gratisliefern</th>
        </tr>
        <?php foreach ($person_array as $Benutzer) : ?>
            <tr>
                <td><?php echo $Benutzer['BENUTZERID']; ?></td>
                <td><?php echo $Benutzer['VORNAME']; ?></td>
                <td><?php echo $Benutzer['NACHNAME']; ?></td>
                <td><?php echo $Benutzer['ADRESSE']; ?></td>
                <td><?php echo $Benutzer['EMAIL']; ?></td>
                <td><?php echo $Benutzer['PROMOCODE']; ?></td>
                <td><?php echo $Benutzer['TELEFONNUMMER']; ?></td>
                <td><?php echo $Benutzer['GEBUEHR']; ?></td>
                <td><?php echo $Benutzer['GRATISLIEFERN'] ? "Ja" : "Nein"; ?></td>
            </tr>
        <?php endforeach; ?>
    </table>
    </div>
</div>
</body>
</html>
