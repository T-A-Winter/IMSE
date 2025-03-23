<?php
session_start();
?>
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <title>Warenkorb Bestätigung</title>
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            margin: 0;
            padding: 0;
            background: url('done.png') no-repeat center center fixed;
            background-size: cover; /* Füllt den gesamten Bildschirm unabhängig von der Größe */
        }

        .container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            max-width: 600px;
            margin: auto;
        }
        p {
            font-size: 18px;
        }
        .message {
            color: #28a745;
            border: 1px solid #28a745;
            padding: 10px;
            border-radius: 5px;
            text-align: center;
        }
        .error {
            color: #dc3545;
            border: 1px solid #dc3545;
        }
        a {
            display: block;
            text-align: center;
            margin-top: 20px;
            background-color: #ff6900;
            color: white;
            padding: 10px 15px;
            border-radius: 5px;
            text-decoration: none;
            font-weight: bold;
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
        <?php if(isset($_SESSION['cart_save_success'])): ?>
            <p class="message"><?php echo htmlspecialchars($_SESSION['cart_save_success']); ?></p>
            <?php unset($_SESSION['cart_save_success']); // Meldung aus der Session entfernen ?>
        <?php else: ?>
            <p class="message error">Es gab ein Problem beim Speichern Ihres Warenkorbs.</p>
        <?php endif; ?>
        <a href="IndexG.php">Weiter einkaufen</a>
    </div>
</body>
</html>
