<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

if(isset($_POST['submitL'])) {
    require_once('DatabaseHelper.php');

    $database = new DatabaseHelper();
    $LieferrantID = '';
    if (isset($_POST['LieferrantID'])) {
        $LieferrantID = $_POST['LieferrantID'];
    }

    $LieferrantName = '';
    if (isset($_POST['LieferrantName'])) {
        $LieferrantName = $_POST['LieferrantName'];
    }

    $FahrzeugTyp = '';
    if (isset($_POST['FahrzeugTyp'])) {
        $FahrzeugTyp = $_POST['FahrzeugTyp'];
    }

    $AppID = '';
    if (isset($_POST['AppID'])) {
        $AppID = $_POST['AppID'];
    }

    $success = $database->insertIntoLieferrant($LieferrantName, $FahrzeugTyp);
    if ($success) {
        echo "Benuzter '{$LieferrantID} {$LieferrantName}' successfully added!'";
    } else {
        echo "Error can't insert Person '{$LieferrantID} {$LieferrantName}'!";
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Add Lieferrant</title>
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
        input, select, button {
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
    </a>
    </div>
<div class="container">
    <a href="index.php" class="back-link">&laquo; Zurück</a>
    <h2>Add Lieferrant:</h2>
    <form method="post" action="addLieferrant.php">
        <div>
            <label for="new_LieferrantName">LieferrantName:</label>
            <input id="new_LieferrantName" name="LieferrantName" type="text" maxlength="20">
        </div>
        <div>
            <label for="new_FahrzeugTyp">FahrzeugTyp:</label>
            <select id="new_FahrzeugTyp" name="FahrzeugTyp">
                <option value="F">F</option>
                <option value="A">A</option>
            </select>
        </div>
        <div>
            <button name="submitL" type="submit">Add Lieferrant</button>
        </div>
    </form>
</div>
</body>
</html>
