<?php
session_start();

error_reporting(E_ALL); 
ini_set('display_errors', 1);

const username = 'a11930767';
const password = 'dbs23';
const con_string = '//oracle19.cs.univie.ac.at:1521/orclcdb';


    define('USERNAME', 'a11930767');
    define('PASSWORD', 'dbs23');
    define('CON_STRING', '//oracle19.cs.univie.ac.at:1521/orclcdb');
    
    $conn = oci_connect(USERNAME, PASSWORD, CON_STRING);
        

    if (!$conn) {
        $error = oci_error();
        die("Datenbankverbindungsfehler: " . $error['message']);
        }

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $userid = $_POST['userid'];
    $email = $_POST['email'];

    $stmt = oci_parse($conn, "SELECT BenutzerID, Email FROM Benutzer WHERE BenutzerID = :userid AND Email = :email");
    oci_bind_by_name($stmt, ':userid', $userid, -1, OCI_B_INT);
    oci_bind_by_name($stmt, ':email', $email, -1, SQLT_CHR);
    oci_execute($stmt);

    if (oci_fetch($stmt)) {
        $_SESSION['user_id'] = $userid;

        if (!empty($_SESSION['warenkorb'])) {
            header("Location: IndexW.php"); // Weiterleitung zur Warenkorb-Seite
            exit();
            }

     else {
        header("Location: IndexG.php"); // Weiterleitung zur Gerichte-Liste
        exit();
    }
}
}

?>

<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #FF8000; /* Hintergrundfarbe auf Orange setzen */
            margin: 0;
            padding: 0;
        }

        .login-form {
            width: 300px;
            margin: 50px auto;
            padding: 30px;
            background: white;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            border-radius: 8px; /* Abgerundete Ecken für das Formular */
        }

        .form-control {
            margin-bottom: 15px;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            width: 100%;
            box-sizing: border-box;
            transition: border-color 0.3s; /* Sanfter Farbübergang bei Fokus */
        }

        .form-control:focus {
            outline: none;
            border-color: #ff6900; /* Grün bei Fokus */
        }

        .submit-button {
            padding: 12px 15px;
            border: none;
            border-radius: 4px;
            color: white;
            background-color: #ff6900;
            cursor: pointer;
            width: 100%;
            transition: background-color 0.3s; /* Sanfter Farbübergang bei Hover */
        }

        .submit-button:hover {
            background-color: #ff6900; /* Dunkleres Grün bei Hover */
        }

        .back-link {
            display: block;
            margin-bottom: 20px;
            color: #ff6900; /* Grün für den Zurück-Link */
            text-decoration: none;
            font-weight: bold;
        }

        .back-link:hover {
            text-decoration: underline;
        }

        .login-form h1 {
            text-align: center;
            color: #333; /* Dunklerer Text für den Formular-Titel */
        }

        .logo {
            text-align: right;
            padding-right: 10px; /* Abstand für das Logo rechts oben */
        }

        .logo img {
            width: 100px; /* Breite des Logos anpassen */
            height: auto; /* Automatische Höhe basierend auf der Breite */
        }

    </style>
</head>
<body>
<div class="logo">
    <a href="index.php" class="logo">
        <img src="Logo.png" alt="Ayran Food Delivery Logo">
    </a>
</div>

    <div class="login-form">
        <a href="index.php" class="back-link">&laquo; Zurück</a>
        <form method="post" action="Login.php">
            <div>
                <label for="userid">Benutzer-ID:</label>
                <input class="form-control" type="text" id="userid" name="userid">
            </div>
            <div>
                <label for="email">E-Mail:</label>
                <input class="form-control" type="email" id="email" name="email">
            </div>
            <div>
                <button class="submit-button" type="submit">Anmelden</button>
            </div>
        </form>
    </div>
</body>
</html>