<?php
if(isset($_POST['submitRD'])) {
    $input_password = '';
    if (isset($_POST['password'])) {
        $input_password = $_POST['password'];
    }
    $correct_password = 'dbs23'; // Das festgelegte Passwort
    if ($input_password === $correct_password) {

    require_once('DatabaseHelper.php');
    $database = new DatabaseHelper();
    $Anschrift = '';
    if (isset($_POST['Anschrift'])) {
        $Anschrift = $_POST['Anschrift'];
    }

    $error_code = $database->deleteRestaurant($Anschrift);
    if ($error_code == 1) {
        echo "Restaurant with Anschrift: '{$Anschrift}' successfully deleted!";
    } else {
        echo "Error can't delete Restaurant with Anschrift: '{$Anschrift}' . Errorcode: {$error_code}";
    }

    }else {
        echo "Incorrect password. Cannot delete Gericht.";
    }
}
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Delete Restaurant</title>
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
<div class="container">
    <a href="index.php" class="logo">
        <img src="Logo.png" alt="Ayran Food Delivery Logo">
    </a>

    <a href="index.php" class="back-link">&laquo; Zurück</a>
    <h2>Delete Restaurant:</h2>
    <form method="post" action="delRestaurant.php">
        <div>
            <label for="del_Anschrift">Anschrift:</label>
            <input id="del_Anschrift" name="Anschrift" type="text" min="1">
        </div>
        <div>
            <label for="upd_password">Password:</label>
            <input id="upd_password" name="password" type="password">
        </div>
        <div>
            <button name="submitRD" type="submit">Delete Restaurant</button>
        </div>
    </form>
</div>
</body>
</html>
