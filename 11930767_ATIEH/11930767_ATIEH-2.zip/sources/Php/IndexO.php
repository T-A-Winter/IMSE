<?php
session_start();
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

require_once('DatabaseHelper.php');
$database = new DatabaseHelper();
$WarenkorbID = '';
if (isset($_GET['WarenkorbID'])) {
    $WarenkorbID = $_GET['WarenkorbID'];
}

$OrderItemID = '';
if (isset($_GET['OrderItemID'])) {
    $OrderItemID = $_GET['OrderItemID'];
}

$GerichtID = '';
if (isset($_GET['GerichtID'])) {
    $GerichtID = $_GET['GerichtID'];
}

$Price = '';
if (isset($_GET['Price'])) {
    $Price = $_GET['Price'];
}

$Quantity = '';
if (isset($_GET['Quantity'])) {
    $Quantity = $_GET['Quantity'];
}

$TotalPriceG = '';
if (isset($_GET['TotalPriceG'])) {
    $TotalPriceG = $_GET['TotalPriceG'];
}


$orderItem_array = $database->selectAllOrderItem($WarenkorbID, $OrderItemID, $GerichtID, $Price, $Quantity, $TotalPriceG);

?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OrderItem</title>
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
            margin-bottom: 20px;
            text-align: center; /* Center align for better visual */
        }
        .nav-link {
            display: inline-block; /* Display as inline-block for proper spacing */
            margin-right: 10px; /* Add some margin to the right for spacing */
            padding: 10px 15px; /* Padding for a larger clickable area */
            background-color: #ff6900; /* A nice green background */
            color: white; /* White text */
            text-decoration: none; /* Remove underline from links */
            border-radius: 5px; /* Rounded corners for a pill-like shape */
            transition: background-color 0.3s ease; /* Smooth background color transition */
        }

        .nav-link:hover {
            background-color: #ff6900; /* Slightly darker green on hover for feedback */
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
    <h1>OrderItem</h1>
    <div class="nav-links">
        <a href="SearchOrderItem.php" class="nav-link">Search</a>
        <a href="IndexW.php" class="nav-link">Warenkorb anzeigen</a>
        <a href="index.php" class="nav-link">Zurück zur Start Seite</a>
    </div>
    <table>
        <thead>
        <tr>
            <th>OrderItemID</th>
            <th>WarenkorbID</th>
            <th>GerichtID</th>
            <th>Price</th>
            <th>Quantity</th>
            <th>TotalPriceG</th>
        </tr>
        </thead>
        <tbody>
        <?php foreach ($orderItem_array as $Warenkorb) : ?>
            <tr>
                <td><?php echo $Warenkorb['ORDERITEMID']; ?></td>
                <td><?php echo $Warenkorb['WARENKORBID']; ?></td>
                <td><?php echo $Warenkorb['GERICHTID']; ?></td>
                <td><?php echo $Warenkorb['PRICE']; ?></td>
                <td><?php echo $Warenkorb['QUANTITY']; ?></td>
                <td><?php echo $Warenkorb['TOTALPRICEG']; ?></td>

            </tr>
        <?php endforeach; ?>
        </tbody>
    </table>
</div>
</body>
</html>
