<?php
require_once('DatabaseHelper.php');

//instantiate DatabaseHelper class
$database = new DatabaseHelper();
if(isset($_POST['submitG'])) {

//Grab variables from POST request


$GerichtID = '';
if (isset($_POST['GerichtID'])) {
    $GerichtID = $_POST['GerichtID'];
}

$RestaurantAnschrift = '';
if (isset($_POST['RestaurantAnschrift'])) {
    $RestaurantAnschrift = $_POST['RestaurantAnschrift'];
}

$GerichtName = '';
if (isset($_POST['GerichtName'])) {
    $GerichtName = $_POST['GerichtName'];
}

$Price = '';
if (isset($_POST['Price'])) {
    $Price = $_POST['Price'];
}

$success = $database->insertIntoGericht($GerichtID, $RestaurantAnschrift, $GerichtName, $Price);

// Check result
if ($success){
    echo "Gericht '{$GerichtID} {$GerichtName}' successfully added!'";
}
else{
    echo "Error can't insert Gericht '{$GerichtID} {$GerichtName}'!";
}
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Add Gericht</title>
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
        h2, label {
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
</div>

<div class="container">
    <a href="index.php" class="back-link">&laquo; Zurück</a>
    <h2>Add Gericht:</h2>
    <form method="post" action="addGericht.php">
        <div>
            <label for="new_GerichtName">GerichtName:</label>
            <input id="new_GerichtName" name="GerichtName" type="text" maxlength="20">
        </div>
        <div>
            <label for="new_Price">Price:</label>
            <input id="new_Price" name="Price" type="number" >
        </div>
        <div>
            <label for="new_RestaurantAnschrift">RestaurantAnschrift:</label>
            <select id="new_RestaurantAnschrift" name="RestaurantAnschrift">
                <?php
                $addresses = $database->getRestaurantAddresses();
                while ($row = oci_fetch_assoc($addresses)) {
                    echo "<option value='" . htmlspecialchars($row['ANSCHRIFT'], ENT_QUOTES, "UTF-8") . "'>"
                        . htmlspecialchars($row['ANSCHRIFT'], ENT_QUOTES, "UTF-8") . "</option>";
                }
                ?>
            </select>
        </div>
        <div>
            <button name="submitG" type="submit">Add Gericht</button>
        </div>
    </form>
</div>
</body>
</html>
