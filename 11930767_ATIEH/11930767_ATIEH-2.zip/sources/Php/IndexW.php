<?php
session_start();
error_reporting(E_ALL);
ini_set('display_errors', 1);

require_once 'Warenkorb.php';
require_once 'DatabaseHelper.php';


$warenkorb = new Warenkorb();
$database = new DatabaseHelper();

if (!isset($_SESSION['user_id'])) {
    $_SESSION['cart_save_error'] = "Sie müssen angemeldet sein, um den Warenkorb zu speichern.";
    header('Location: Login.php'); 
    exit();
}

function isSameRestaurant($warenkorbItems, $currentRestaurant) {
    foreach ($warenkorbItems as $item) {
        if ($item['RestaurantAnschrift'] !== $currentRestaurant) {
            return false;
        }
    }
    return true;
}

if (isset($_POST['add_to_warenkorb'])) {
    $warenkorbItems = isset($_SESSION['warenkorb']) ? $_SESSION['warenkorb'] : [];
    $currentRestaurant = $_POST['RestaurantAnschrift'];

    if (!empty($warenkorbItems) && !isSameRestaurant($warenkorbItems, $currentRestaurant)) {
        $_SESSION['warenkorb_error'] = "Der Warenkorb enthält bereits Gerichte aus einem anderen Restaurant.";
        $_SESSION['attempted_addition'] = $_POST;
        $_SESSION['warenkorb_restaurant'] = $_POST['RestaurantAnschrift'];
        header('Location: confirm_switch_or_cancel.php');
        exit();
    } else {
        $warenkorb->add($_POST['GerichtID'], $_POST['GerichtName'], $_POST['Price'], $currentRestaurant, isset($_POST['liefernKosten']) ? $_POST['liefernKosten'] : 0);
        $_SESSION['last_restaurant_address'] = $currentRestaurant;
    }
}

if (isset($_POST['save_cart']) && isset($_SESSION['warenkorb'])) {
    echo "Attempting to save cart...<br>";

    $userID = $_SESSION['user_id'];
    $items = $_SESSION['warenkorb'];
    $success = $database->insertWarenkorb($userID, $items);
    if ($success) {
        echo "Cart saved successfully.<br>";
    } else {
        echo "Failed to save cart.<br>";
    }

    if ($success) {
        $_SESSION['cart_save_success'] = "Warenkorb erfolgreich gespeichert.";
        $_SESSION['warenkorb'] = array();
        header('Location: cart_confirmation.php'); 
        exit();
    } else {
        $_SESSION['cart_save_error'] = "Fehler beim Speichern des Warenkorbs.";
        //header('Location: IndexW.php');
        exit();
    }
}

foreach ($_SESSION['warenkorb'] as $key => $item) {
    if (empty($item['GerichtName']) || empty($item['RestaurantAnschrift']) || !isset($item['Price'])) {
        unset($_SESSION['warenkorb'][$key]);
    }
}
$_SESSION['warenkorb'] = array_values($_SESSION['warenkorb']); // Reindex the array


$liefernKosten = isset($_POST['liefernKosten']) ? $_POST['liefernKosten'] : 0; // Default to 0 if not set


if (isset($_POST['remove_from_warenkorb']) && isset($_POST['GerichtName'])) {
    $warenkorb->remove($_POST['GerichtName']);
}

$isPrime = $database->isPrimeKunde($_SESSION['user_id']);
$liefernKosten = $isPrime ? 0 : 3; // Set delivery cost to 3 if not a prime customer

$warenkorbItems = $warenkorb->getItems();
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
        .cart-item {
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .cart-item button {
            margin-left: auto;
        }
        .back-link, .checkout-btn {
            display: block;
            width: max-content;
            margin: 20px auto;
            text-align: center;
            padding: 10px 15px;
            background-color: #ff6900;
            color: white;
            text-decoration: none;
            border-radius: 5px;
        }
        .back-link:hover, .checkout-btn:hover {
            background-color: #ff6900;
        }
        .checkout-btn {
            background-color: #ff6900; /* Blue */
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
    <h1>Ihr Warenkorb</h1>

    <?php if (count($warenkorbItems) > 0): ?>
        <ul>
            <?php foreach ($warenkorbItems as $item): ?>
                <li class="cart-item">
                    <?php
                    $gerichtName = isset($item['GerichtName']) ? htmlspecialchars($item['GerichtName']) : 'Unbekanntes Gericht';
                    $price = isset($item['Price']) ? htmlspecialchars($item['Price']) : '0';
                    $quantity = isset($item['Quantity']) ? htmlspecialchars($item['Quantity']) : '0';
                    $restaurantAnschrift = isset($item['RestaurantAnschrift']) ? htmlspecialchars($item['RestaurantAnschrift']) : 'Unbekannte Adresse';

                    echo $gerichtName . " - " . $price . " € (Anzahl: " . $quantity . " - " . $restaurantAnschrift;

                    if (!$isPrime && isset($liefernKosten)) { // Only add this line if the user is not a prime customer and $liefernKosten is set
                        echo " - Lieferkosten: " . htmlspecialchars($liefernKosten) . " €";
                    }
                    echo ")";
                    ?>
                    <form method='post' action='IndexW.php' style='display: inline;'>
                        <input type='hidden' name='GerichtName' value='<?php echo htmlspecialchars($item['GerichtName']); ?>'>
                        <button type='submit' name='remove_from_warenkorb'>Entfernen</button>
                    </form>

                </li>
            <?php endforeach; ?>
        </ul>
        <form method="post" action="IndexW.php" style="text-align:center;">
            <button type="submit" class="checkout-btn" name="save_cart">Warenkorb speichern</button>
        </form>
    <?php else: ?>
        <p>Ihr Warenkorb ist leer.</p>
    <?php endif; ?>

    <a href='IndexG.php?RestaurantAnschrift=<?php echo isset($_SESSION['last_restaurant_address']) ? urlencode($_SESSION['last_restaurant_address']) : ''; ?>' class="back-link">Zurück zur Gerichteliste</a>
</div>
</body>
</html>
