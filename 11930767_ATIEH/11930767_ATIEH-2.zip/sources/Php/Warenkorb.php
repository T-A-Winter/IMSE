<?php
class Warenkorb {

    public function __construct() {
        if (!isset($_SESSION['warenkorb'])) {
            $_SESSION['warenkorb'] = array();
        }
    }

    public function add($gerichtID, $gerichtName, $price, $RestaurantAnschrift, $liefernKosten) {
        $isAlreadyInWarenkorb = false;
        foreach ($_SESSION['warenkorb'] as &$item) {
            if ($item['GerichtID'] == $gerichtID && $item['RestaurantAnschrift'] == $RestaurantAnschrift) {
                $item['Quantity'] += 1;
                $isAlreadyInWarenkorb = true;
                break;
            }
        }
        unset($item);
        if (!$isAlreadyInWarenkorb) {
            $_SESSION['warenkorb'][] = array(
                'GerichtID' => $gerichtID,
                'GerichtName' => $gerichtName,
                'Price' => $price,
                'RestaurantAnschrift' => $RestaurantAnschrift,
                'Quantity' => 1,
                'LiefernKosten' =>$liefernKosten
            );
        }
    }

    public function remove($gerichtName) {
        foreach ($_SESSION['warenkorb'] as $key => &$item) {
            if ($item['GerichtName'] == $gerichtName) {
                if ($item['Quantity'] > 1) {
                    $item['Quantity']--;
                } else{
                    unset($_SESSION['warenkorb'][$key]);
                }
                break;
            }
        }
        unset($item);
        $_SESSION['warenkorb'] = array_values($_SESSION['warenkorb']);
    }

    public function getItems() {
        return $_SESSION['warenkorb'];
    }
}
?>
