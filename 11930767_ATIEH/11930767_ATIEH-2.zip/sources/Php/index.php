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

//Fetch data from database
$person_array = $database->selectBenutzer($BenutzerID, $Vorname, $Nachname, $Adresse, $Email, $PromoCode, $Telefonnummer, $premiumFilter);
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HamzApp</title>
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            margin: 0;
            padding: 0;
            background: url('back.png') no-repeat center center fixed;
            background-size: cover; /* Füllt den gesamten Bildschirm unabhängig von der Größe */
        }

        .container {
            background: none;
            padding: 20px;
            margin: 20px auto;
            max-width: 1000px;
        }

        .container h1, .container .group {
            background: rgba(255, 255, 255, 0.1); /* Leicht transparenter Hintergrund hinter dem Text */
            padding: 10px;
            border-radius: 5px;
        }

        h1 {
            text-align: center;
            color: #fff;
            font-size: 2.5em;
        }

        h2 {
            text-align: center;
            color: #fff;
            font-size: 1.5em;
        }
        .group {
            background-color: #fff;
            margin-bottom: 20px;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0);
        }

        .group a {
            background-color: #ff6900;
            color: white;
            padding: 10px 15px;
            display: block;
            margin: 10px 0;
            text-align: center;
            border-radius: 5px;
            transition: all 0.3s ease-in-out;
        }

        .group a:hover {
            background-color: #e65a00;
            box-shadow: 0 4px 8px rgb(255, 255, 255);
            transform: translateY(-2px);
        }

        /* Responsives Design für Mobilgeräte */
        @media (max-width: 768px) {
            .container {
                width: 90%;
                padding: 10px;
            }

            h1 {
                font-size: 2em;
            }
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
    <img src="Logo.png" alt="Ayran Food Delivery Logo">
</div>

<div class="container">
    <h1>Ayran Food Delivery</h1>
    <div class="group">
        <h2>Benutzerverwaltung</h2>
        <a href="Login.php">Anmeldung</a>
        <a href="Logout.php">Abmeldung</a>
        <a href="addPerson.php">Add Benutzer</a>
        <a href="delPerson.php">Delete Benutzer</a>
        <a href="search.php">Search Benutzer</a>
    </div>
    <div class="group">
        <h2>Restaurantverwaltung</h2>
        <a href="IndexR.php">Restaurant</a>
        <a href="addRestaurant.php">Add Restaurant</a>
        <a href="delRestaurant.php">Delete Restaurant</a>
        <a href="searchRestaurant.php">Search Restaurant</a>
        <a href="UpdateR.php">Update Restaurant</a>
        <a href="ProcedureR.php">Durchschnittspreis</a>
    </div>
    <div class="group">
        <h2>Bestellungsverwaltung</h2>
        <a href="IndexO.php">OrderItem</a>
        <a href="IndexWW.php">Warenkorb</a>
        <a href="IndexW.php">Warenkorb anzeigen</a>
        <a href="SearchOrderItem.php">Search OrderItem</a>
        <a href="SearchWarenkorb.php">Search Warenkorb</a>
    </div>
    <div class="group">
        <h2>Speisekartenverwaltung</h2>
        <a href="addGericht.php">Add Gericht</a>
        <a href="delGericht.php">Delete Gericht</a>
        <a href="SearchGericht.php">Search Gericht</a>
        <a href="UpdateG.php">Update Gericht</a>
    </div>
    <div class="group">
        <h2>Lieferantenverwaltung</h2>
        <a href="addLieferrant.php">Add Lieferrant</a>
        <a href="delLieferrant.php">Delete Lieferrant</a>
        <a href="SearchLieferrant.php">Search Lieferrant</a>
    </div>
</div>
</body>
</html>

