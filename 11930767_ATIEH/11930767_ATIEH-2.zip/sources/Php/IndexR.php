<?php

session_start();

ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);
require_once('DatabaseHelper.php');
$database = new DatabaseHelper();

$RestaurantName = '';
if (isset($_GET['RestaurantName'])) {
    $RestaurantName = $_GET['RestaurantName'];
}

$Anschrift = '';
if (isset($_GET['Anschrift'])) {
    $Anschrift = $_GET['Anschrift'];
}

$Oeffnungszeiten = '';
if (isset($_GET['Oeffnungszeiten'])) {
    $Oeffnungszeiten = $_GET['Oeffnungszeiten'];
}

$Ort = '';
if (isset($_GET['Ort'])) {
    $Ort = $_GET['Ort'];
}

$Plz = '';
if (isset($_GET['Plz'])) {
    $Plz = $_GET['Plz'];
}

$restaurant_array = $database->selectAllRestaurant($RestaurantName, $Anschrift, $Oeffnungszeiten, $Ort, $Plz);

?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Restaurant Liste</title>
    <link href="https://fonts.googleapis.com/css?family=Roboto:400,700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            background-color: #FF8000;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 20px auto;
            padding: 20px;
        }
        .card {
            background: #fff;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            transition: box-shadow 0.3s ease-in-out;
        }
        .card:hover {
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
        }
        .card-header {
            background-color: #ff6900;
            color: white;
            padding: 10px 15px;
            font-size: 1.25em;
            font-weight: bold;
        }
        .card-body {
            padding: 15px;
            line-height: 1.6;
        }
        .button {
            background-color: #ff6900;
            color: white;
            border: none;
            padding: 10px 20px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 4px;
            transition: background-color 0.3s;
        }
        .button:hover {
            background-color: #ff6900;
        }
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
        }
        .back-link {
            color: #000000;
            text-decoration: none;
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
    <h1>Restaurants</h1>
    <?php foreach ($restaurant_array as $Restaurant) : ?>
        <div class="card">
            <div class="card-header">
                <?php echo htmlspecialchars($Restaurant['RESTAURANTNAME']); ?>
            </div>
            <div class="card-body">
                <p>Anschrift: <?php echo htmlspecialchars($Restaurant['ANSCHRIFT']); ?></p>
                <p>Öffnungszeiten: <?php echo htmlspecialchars($Restaurant['OEFFNUNGSZEITEN']); ?></p>
                <p>Ort: <?php echo htmlspecialchars($Restaurant['ORT']); ?></p>
                <p>PLZ: <?php echo htmlspecialchars($Restaurant['PLZ']); ?></p>
                <a href="IndexG.php?RestaurantAnschrift=<?php echo urlencode($Restaurant['ANSCHRIFT']); ?>" class="button">Gerichte anzeigen</a>
            </div>
        </div>
    <?php endforeach; ?>
</div>
</body>
</html>
