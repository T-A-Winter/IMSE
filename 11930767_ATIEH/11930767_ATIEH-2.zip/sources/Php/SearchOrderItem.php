<?php
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

$warenkorb_array = $database->selectOrderItem($WarenkorbID, $OrderItemID, $GerichtID, $Price, $Quantity, $TotalPriceG);
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Search OrderItem</title>
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
        }.logo {
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
    <h1>OrderItem Search:</h1>
    <form method="get">
        <div>
            <label for="OrderItemID">OrderItemID:</label>
            <input id="OrderItemID" name="OrderItemID" type="text" value='<?php echo $OrderItemID; ?>' min="0">
        </div>
        <div>
            <label for="WarenkorbID">WarenkorbID:</label>
            <input id="WarenkorbID" name="WarenkorbID" type="text" value='<?php echo $WarenkorbID; ?>'>
        </div>
        <div>
            <label for="GerichtID">GerichtID:</label>
            <input id="GerichtID" name="GerichtID" type="text" value='<?php echo $GerichtID; ?>'>
        </div>

        <div>
            <button id='submit' type='submit'>Search</button>
        </div>
    </form>
    <br>
    <hr>

    <!-- Search result -->
    <h2>OrderItem Search Result:</h2>
    <table>
        <tr>
            <th>OrderItemID</th>
            <th>WarenkorbID</th>
            <th>GerichtID</th>
            <th>Price</th>
            <th>Quantity</th>
            <th>TotalPriceG</th>
        </tr>
        <?php foreach ($warenkorb_array as $Warenkorb) : ?>
            <tr>
                <td><?php echo $Warenkorb['ORDERITEMID']; ?></td>
                <td><?php echo $Warenkorb['WARENKORBID']; ?></td>
                <td><?php echo $Warenkorb['GERICHTID']; ?></td>
                <td><?php echo $Warenkorb['PRICE']; ?></td>
                <td><?php echo $Warenkorb['QUANTITY']; ?></td>
                <td><?php echo $Warenkorb['TOTALPRICEG']; ?></td>

            </tr>
        <?php endforeach; ?>
    </table>
</div>
</body>
</html>
