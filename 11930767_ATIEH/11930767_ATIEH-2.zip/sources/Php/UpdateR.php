<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

require_once('DatabaseHelper.php');
$database = new DatabaseHelper();

$success = "";
$error = "";

if (isset($_POST['submit'])) {
$input_password = '';
if (isset($_POST['password'])) {
    $input_password = $_POST['password'];
}
$correct_password = 'dbs23'; // Das festgelegte Passwort

if ($input_password === $correct_password) {
    $Anschrift = $_POST['Anschrift'];
    $newName = !empty($_POST['newName']) ? $_POST['newName'] : null;
    $newOeffnungszeiten = !empty($_POST['newOeffnungszeiten']) ? $_POST['newOeffnungszeiten'] : null;

    if ($database->updateRestaurant($Anschrift, $newName, $newOeffnungszeiten)) {
        $success = "Restaurant successfully updated.";
    } else {
        $error = "Error updating Restaurant.";
    }
} else {
    echo "Incorrect password. Cannot delete Gericht.";
    }
}

?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Update Restaurant</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #FF8000;
            margin: 0;
            padding: 0;
        }
        .container {
            width: 50%;
            margin: 40px auto;
            background: white;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        label {
            display: block;
            margin: 15px 0 5px;
        }
        input[type="text"], input[type="number"], input[type="password"]  {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
            margin-bottom: 20px;
        }
        button {
            width: 100%;
            padding: 10px;
            background-color: #ff6900;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover {
            background-color: #ff6900;
        }
        .back-link {
            color: #ff6900;
            text-decoration: none;
        }

        .message {
            text-align: center;
            margin: 10px 0;
        }
        .success {
            color: green;
        }
        .error {
            color: red;
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
    <h1>Update Restaurant</h1>
    <?php
    if ($success) echo "<p style='color: green;'>$success</p>";
    if ($error) echo "<p style='color: red;'>$error</p>";
    ?>
    <form method="post">
        <div>
            <label for="Anschrift">Anschrift:</label>
            <input id="Anschrift" name="Anschrift" type="text" required>
        </div>
        <div>
            <label for="newName">Neuer Name:</label>
            <input id="newName" name="newName" type="text">
        </div>
        <div>
            <label for="newOeffnungszeiten">Neue Öffnungszeiten:</label>
            <input id="newOeffnungszeiten" name="newOeffnungszeiten" type="text">
        </div>
        <div>
            <label for="upd_password">Password:</label>
            <input id="upd_password" name="password" type="password">
        </div>
        <div>
            <button type="submit" name="submit">Update Restaurant</button>
        </div>
    </form>
</div>
</body>
</html>
