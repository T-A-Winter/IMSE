<?php

session_start(); // Dies muss ganz oben stehen, bevor irgendwelche Ausgaben erfolgen.

ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);
require_once('DatabaseHelper.php');
$database = new DatabaseHelper();

$GerichtID = '';
if (isset($_GET['GerichtID'])) {
    $GerichtID = $_GET['GerichtID'];
}

$RestaurantAnschrift = '';
if (isset($_GET['RestaurantAnschrift'])) {
    $RestaurantAnschrift = $_GET['RestaurantAnschrift'];
}

$GerichtName = '';
if (isset($_GET['GerichtName'])) {
    $GerichtName = $_GET['GerichtName'];
}

$Price = '';
if (isset($_GET['Price'])) {
    $Price = $_GET['Price'];
}

$liefernKosten = 3;
if (isset($_SESSION['user_id'])) {
    if ($database->isPrimeKunde($_SESSION['user_id'])) {
        $liefernKosten = 0;
    }
}
$gericht_array = $database->selectGericht($GerichtID, $RestaurantAnschrift, $GerichtName, $Price);

if (!isset($gerichte_array)) {
    $gerichte_array = array();
}
$gerichte_array = $database->selectGerichteByAnschrift($RestaurantAnschrift);

if (isset($_POST['add_to_warenkorb'])) {
    $gerichtToAdd = [
        'GerichtID' => $_POST['GerichtID'],
        'GerichtName' => $_POST['GerichtName'],
        'Price' => $_POST['Price']
    ];
    if (!isset($_SESSION['warenkorb'])) {
        $_SESSION['warenkorb'] = [];
    }

    $_SESSION['warenkorb'][] = $gerichtToAdd;
    header('Location: IndexG.php');
    exit();
}

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gerichte für Restaurant</title>
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
        h1, h2, label, th, td, a {
            color: #333;
            text-decoration: none;
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
        .button {
            padding: 10px 15px;
            background-color: #ff6900;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        .button:hover {
            background-color: #ff6900;
        }
        .link-button {
            color: #007bff;
            text-decoration: none;
        }
        .link-button:hover {
            text-decoration: underline;
        }
        .nav-links {
            text-align: center;
            margin-bottom: 20px;
        }
        .nav-link {
            display: inline-block;
            margin: 0 10px;
            padding: 10px 15px;
            background-color: #ff6900;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            transition: background-color 0.3s;
        }

        .nav-link:hover {
            background-color: #ff6900;
        }

        .centered-title {
            text-align: center; /* Zentriert den Text horizontal */
            margin-top: 20px;
            margin-bottom: 20px;
        }
        .back-link {
            color: #ff6900;
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
    <h1 class="centered-title">Willkommen</h1>
    <div class="nav-links">
        <a href="index.php" class="nav-link">Home</a>
        <a href="SearchGericht.php" class="nav-link">Gerichte und Restaurants suchen</a>
        <a href="IndexW.php" class="nav-link">Warenkorb anzeigen</a>
        <a href="IndexR.php" class="nav-link">Alle Restaurants anzeigen</a>
        <a href="Logout.php" class="nav-link">Abmeldung</a>
</div>

    <?php if (!empty($gerichte_array)): ?>
        <h2>Gerichte</h2>
        <table>
            <thead>
                <tr>
                    <th>GerichtID</th>
                    <th>RestaurantAnschrift</th>
                    <th>GerichtName</th>
                    <th>Price</th>
                    <th>Add To</th>
                </tr>
            </thead>
            <tbody>
            <?php foreach ($gerichte_array as $Gericht): ?>
                <tr>
                    <td><?php echo htmlspecialchars($Gericht['GERICHTID']); ?></td>
                    <td><?php echo htmlspecialchars($Gericht['RESTAURANTANSCHRIFT']); ?></td>
                    <td><?php echo htmlspecialchars($Gericht['GERICHTNAME']); ?></td>
                    <td><?php echo htmlspecialchars($Gericht['PRICE']); ?></td>
                    <td>
                        <form method="post" action="IndexW.php">
                            <input type="hidden" name="GerichtID" value="<?php echo htmlspecialchars($Gericht['GERICHTID']); ?>">
                            <input type="hidden" name="RestaurantAnschrift" value="<?php echo htmlspecialchars($Gericht['RESTAURANTANSCHRIFT']); ?>">
                            <input type="hidden" name="GerichtName" value="<?php echo htmlspecialchars($Gericht['GERICHTNAME']); ?>">
                            <input type="hidden" name="Price" value="<?php echo htmlspecialchars($Gericht['PRICE']); ?>">
                            <input type="hidden" name="liefernKosten" value="<?php echo $liefernKosten; ?>">
                            <input type="submit" class="button" name="add_to_warenkorb" value="Zum Warenkorb hinzufügen">
                        </form>
                    </td>
                </tr>
            <?php endforeach; ?>
            </tbody>
        </table>
    
    <?php endif; ?>
</div>
</body>
</html>
