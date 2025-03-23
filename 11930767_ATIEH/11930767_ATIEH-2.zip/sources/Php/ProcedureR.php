<?php
ini_set('display_errors', 1);
error_reporting(E_ALL);

require_once('DatabaseHelper.php');
$database = new DatabaseHelper();

$avgPrice = null;
$restaurantAnschrift = '';
$addresses = $database->getRestaurantAddressesA(); // Stellen Sie sicher, dass diese Methode definiert ist

if ($_SERVER["REQUEST_METHOD"] == "POST") {
    $restaurantAnschrift = $_POST['restaurantAnschrift'];
    $avgPrice = $database->getAveragePrice($restaurantAnschrift);
}
?>

<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>Durchschnittspreis Abfrage</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #FF8000;
            margin: 0;
            padding: 20px;
        }
        .container {
            background-color: #ffffff;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            border-radius: 5px;
        }
        select, input[type="submit"] {
            width: 100%;
            padding: 10px;
            margin-top: 5px;
            margin-bottom: 20px;
            border-radius: 5px;
            border: 1px solid #ddd;
        }
        input[type="submit"] {
            background-color: #ff6900;
            color: white;
            font-size: 16px;
            border: none;
            cursor: pointer;
        }
        input[type="submit"]:hover {
            background-color: #ff6900;
        }

        .back-link {
            color: #ff6900;
            text-decoration: none;
        }
        .back-link:hover {
            text-decoration: underline;
        }
        .result {
            background-color: #e9e9e9;
            padding: 10px;
            border-radius: 5px;
        }  .logo {
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
    <h2>Durchschnittspreis der Gerichte eines Restaurants abfragen</h2>
    <form method="post">
        <div>
            <label for="new_RestaurantAnschrift">RestaurantAnschrift:</label>
            <select id="new_RestaurantAnschrift" name="restaurantAnschrift">
                <?php foreach ($addresses as $adresse): ?>
                    <option value="<?= htmlspecialchars($adresse, ENT_QUOTES, 'UTF-8') ?>" <?= $adresse === $restaurantAnschrift ? 'selected' : '' ?>>
                        <?= htmlspecialchars($adresse, ENT_QUOTES, 'UTF-8') ?>
                    </option>
                <?php endforeach; ?>
            </select>
        </div>
        <input type="submit" value="Durchschnittspreis abfragen">
    </form>
    <?php if ($_SERVER["REQUEST_METHOD"] == "POST"): ?>
        <div class="result">
            Durchschnittspreis der Gerichte im Restaurant: <?= htmlspecialchars($avgPrice) ?>
        </div>
    <?php endif; ?>
</div>

</body>
</html>
