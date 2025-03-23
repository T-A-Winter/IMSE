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

$BenutzerID = '';
if (isset($_GET['BenutzerID'])) {
    $BenutzerID = $_GET['BenutzerID'];
}

$ResturantAnschrift = '';
if (isset($_GET['ResturantAnschrift'])) {
    $ResturantAnschrift = $_GET['ResturantAnschrift'];
}

$LiefernKosten = '';
if (isset($_GET['LiefernKosten'])) {
    $LiefernKosten = $_GET['LiefernKosten'];
}
$warenkorb_array = $database->selectWarenkorb($WarenkorbID, $BenutzerID, $ResturantAnschrift, $LiefernKosten);
?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Search Warenkorb</title>
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
    <h1>Warenkorb Search:</h1>
    <form method="get">
        <div>
            <label for="WarenkorbID">WarenkorbID:</label>
            <input id="WarenkorbID" name="WarenkorbID" type="text" value='<?php echo $WarenkorbID; ?>' min="0">
        </div>
        <div>
            <label for="BenutzerID">BenutzerID:</label>
            <input id="BenutzerID" name="BenutzerID" type="text" value='<?php echo $BenutzerID; ?>'>
        </div>
        <div>
            <label for="ResturantAnschrift">ResturantAnschrift:</label>
            <input id="ResturantAnschrift" name="ResturantAnschrift" type="text" value='<?php echo $ResturantAnschrift; ?>'>
        </div>
        <div>
            <button id='submit' type='submit'>Search</button>
        </div>
    </form>
    <br>
    <hr>

    <!-- Search result -->
    <h2>Warenkorb Search Result:</h2>
    <table>
        <tr>
            <th>WarenkorbID</th>
            <th>BenutzerID</th>
            <th>ResturantAnschrift</th>
            <th>LiefernKosten</th>

        </tr>
        <?php foreach ($warenkorb_array as $Warenkorb) : ?>
            <tr>
                <td><?php echo $Warenkorb['WARENKORBID']; ?></td>
                <td><?php echo $Warenkorb['BENUTZERID']; ?></td>
                <td><?php echo $Warenkorb['RESTURANTANSCHRIFT']; ?></td>
                <td><?php echo $Warenkorb['LIEFERNKOSTEN']; ?></td>
            </tr>
        <?php endforeach; ?>
    </table>
</div>
</body>
</html>
