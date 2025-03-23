<?php
session_start();

require_once 'Warenkorb.php';
require_once 'DatabaseHelper.php';

$warenkorb = new Warenkorb();
$database = new DatabaseHelper();

// Prüfen Sie, ob der 'warenkorb_error' gesetzt wurde
$warenkorbError = isset($_SESSION['warenkorb_error']) ? $_SESSION['warenkorb_error'] : 'Es gab ein Problem.';

if (isset($_POST['switch_and_add'])) {
    $_SESSION['warenkorb'] = []; // Leere den Warenkorb
    $attemptedAddition = isset($_SESSION['attempted_addition']) ? $_SESSION['attempted_addition'] : null;
    if ($attemptedAddition) {
        $warenkorb->add(
            $attemptedAddition['GerichtID'],
            $attemptedAddition['GerichtName'],
            $attemptedAddition['Price'],
            $attemptedAddition['RestaurantAnschrift'],
            isset($attemptedAddition['LiefernKosten']) ? $attemptedAddition['LiefernKosten'] : 0
        );
    }
    unset($_SESSION['attempted_addition']);
    header('Location: IndexW.php');
    exit();
}

if (isset($_POST['cancel'])) {
    $redirectLocation = 'IndexG.php';
    if (isset($_SESSION['warenkorb_restaurant'])) {
        $redirectLocation .= '?RestaurantAnschrift=' . urlencode($_SESSION['warenkorb_restaurant']);
    }
    header("Location: $redirectLocation");
    exit();
}

?>
<!DOCTYPE html>
<html lang='de'>
<head>
    <meta charset='UTF-8'>
    <title>Warenkorb</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #FF8000;
            margin: 0;
            padding: 20px;
        }
        .container {
            width: 80%;
            margin: auto;
            background: white;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #000000;
            text-align: center;
        }
        ul {
            list-style-type: none;
            padding: 0;
        }
        li {
            background-color: #fff;
            margin-bottom: 10px;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        button {
            padding: 10px 15px;
            background-color: #ff6900;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin-left: 10px;
        }
        button:hover {
            background-color: #ff6900;
        }
        .cart-item button {
            margin-left: auto;
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
    <h1>Warenkorb wechseln oder abbrechen</h1>
    <p><?php echo $warenkorbError; ?></p>
    <form method="post" action="">
        <button type="submit" name="switch_and_add">Warenkorb leeren und neues Gericht hinzufügen</button>
        <button type="submit" name="cancel">Abbrechen</button>
    </form>
</div>
</body>
</html>
