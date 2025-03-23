<?php
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

$rastaurant_array = $database->selectRestaurant($RestaurantName, $Anschrift, $Oeffnungszeiten, $Ort, $Plz);
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Search Restaurant</title>
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
    <h1>Restaurant Search:</h1>
    <form method="get">
        <div>
            <label for="Anschrift">Anschrift:</label>
            <input id="Anschrift" name="Anschrift" type="text" value='<?php echo $Anschrift; ?>' min="0">
        </div>
        <div>
            <label for="RestaurantName">RestaurantName:</label>
            <input id="RestaurantName" name="RestaurantName" type="text" value='<?php echo $RestaurantName; ?>'>
        </div>
        <div>
            <label for="Oeffnungszeiten">Oeffnungszeiten:</label>
            <input id="Oeffnungszeiten" name="Oeffnungszeiten" type="text" value='<?php echo $Oeffnungszeiten; ?>'>
        </div>
        <div>
            <label for="Ort">Ort:</label>
            <input id="Ort" name="Ort" type="text" value='<?php echo $Ort; ?>'>
        </div>
        <div>
            <label for="Plz">Plz:</label>
            <input id="Plz" name="Plz" type="text" value='<?php echo $Plz; ?>'>
        </div>

        <div>
            <button id='submit' type='submit'>Search</button>
        </div>
    </form>
    <br>
    <hr>

    <!-- Search result -->
    <h2>Restaurant Search Result:</h2>
    <table>
        <tr>
            <th>RestaurantName</th>
            <th>Anschrift</th>
            <th>Oeffnungszeiten</th>
            <th>Ort</th>
            <th>Plz</th>
        </tr>
        <?php foreach ($rastaurant_array as $Restaurant) : ?>
            <tr>
                <td><?php echo $Restaurant['RESTAURANTNAME']; ?></td>
                <td><?php echo $Restaurant['ANSCHRIFT']; ?></td>
                <td><?php echo $Restaurant['OEFFNUNGSZEITEN']; ?></td>
                <td><?php echo $Restaurant['ORT']; ?></td>
                <td><?php echo $Restaurant['PLZ']; ?></td>
            </tr>
        <?php endforeach; ?>
    </table>
</div>
</body>
</html>
