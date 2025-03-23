import java.sql.*;
import java.util.Map;
import java.util.HashMap;
import java.util.concurrent.ThreadLocalRandom;
import java.util.Random;
import java.math.BigDecimal;
import java.util.List;
import java.util.ArrayList;
import java.util.Collections;


public class JavaSqlExample {
  public static void main(String args[]) {
    try {
      Class.forName("oracle.jdbc.driver.OracleDriver");

      String database = "jdbc:oracle:thin:@oracle19.cs.univie.ac.at:1521:orclcdb";
      String user = "a11930767";
      String pass = "dbs23";

      Connection con = DriverManager.getConnection(database, user, pass);
      PreparedStatement pstmtBenutzer = null;
      Statement stmtApp = null;
      PreparedStatement pstmtRestaurant = null;
      PreparedStatement pstmtGericht = null;
      PreparedStatement pstmtLieferrant = null;
      PreparedStatement pstmtKochen = null;
      PreparedStatement pstmtWarenkorb = null;
      PreparedStatement pstmtOrderItem = null; // Declare pstmtOrderItem here

      try{
       con.setAutoCommit(false);
       String insertSqlBenutzer = "INSERT INTO Benutzer (Vorname, Nachname, Adresse, Email, PromoCode, Telefonnummer, Gebuehr, GratisLiefern) VALUES(?, ?, ?, ?, ?, ?, ?, ?)";
       String insertSqlPrimeKunde = "INSERT INTO PrimeKunde (PrimeID, Dauer, Beginn, Gebuehr) VALUES(?, ?, ?, ?)";
       stmtApp = con.createStatement();
       String insertSqlApp = "INSERT INTO App (AppID, AppName, Version) VALUES(1, 'HamzApp', '1.0.0')";
       int rowsAffected = stmtApp.executeUpdate(insertSqlApp);
       String insertSqlRestaurant = "INSERT INTO Restaurant (RestaurantName, Anschrift, Oeffnungszeiten, Ort, Plz)  VALUES(?, ?, ?, ?, ?)";
       String insertSqlGericht = "INSERT INTO Gericht (RestaurantAnschrift, GerichtName, Price)  VALUES(?, ?, ?)";
       String insertSqlLieferrant = "INSERT INTO Lieferrant (LieferrantID, LieferrantName, FahrzeugTyp)  VALUES(?, ?, ?)";
       String insertSqlKochen = "INSERT INTO Kochen (GerichtID, RestaurantAnschrift)  VALUES(?, ?)";

                             // Retrieve necessary data from Benutzer, Restaurant, and Gericht tables
                             List<Integer> benutzerIds = new ArrayList<>();
                             List<String> restaurantAnschrifts = new ArrayList<>();
                             List<Integer> gerichtIds = new ArrayList<>();
                             List<Integer> gerichtPrices = new ArrayList<>();
                             List<Integer> warenkorbIds = new ArrayList<>();

//Benutzer
       try {
        con.setAutoCommit(false);
        pstmtBenutzer = con.prepareStatement(insertSqlBenutzer);
        Random random = new Random();

        for (int i = 1; i <= 1000; i++) {
          pstmtBenutzer.setString(1, "Vorname" + i); // Vorname
          pstmtBenutzer.setString(2, "Nachname" + i); // Nachname
          pstmtBenutzer.setString(3, "Adresse" + i); // Adresse
          pstmtBenutzer.setString(4, "email" + i + "@example.com"); // Email
          pstmtBenutzer.setString(5, "PROMO" + (1000 + random.nextInt(9000))); // PromoCode
          pstmtBenutzer.setString(6, "012345" + (1000 + random.nextInt(9000))); // Telefonnummer

                  if (i % 10 < 4) { // 40% Wahrscheinlichkeit
                      pstmtBenutzer.setBigDecimal(7, new BigDecimal("15.00")); // Gebuehr
                      pstmtBenutzer.setInt(8, 1); // GratisLiefern
                  } else {
                      pstmtBenutzer.setBigDecimal(7, new BigDecimal("0.00")); // Gebuehr für nicht PrimeKunden
                      pstmtBenutzer.setInt(8, 0); // GratisLiefern für nicht PrimeKunden
                  }

          pstmtBenutzer.addBatch();
          if (i % 100 == 0) { // Führen Sie das Batch alle 100 Inserts aus
            int[] resultBenuzter = pstmtBenutzer.executeBatch();
              pstmtBenutzer.clearBatch();
          }
      }
      con.commit();
    } catch (SQLException e) {
      e.printStackTrace();
      try {
          if (con != null) {
              con.rollback();
          }
      } catch (SQLException ex) {
          ex.printStackTrace();
      }
  }

//Restuants
try {
  String[] openingTimes = {"09:30", "10:00", "10:30", "11:00", "11:30", "12:00"};
  con.setAutoCommit(false);
  pstmtRestaurant = con.prepareStatement(insertSqlRestaurant);
  Random random = new Random();
  for (int i = 1; i <= 350; i++) {
    pstmtRestaurant.setString(1, "Restaurant" + i); // Name
    pstmtRestaurant.setString(2, "Anschrift" + i); // Anschrift
    String randomOpeningTime = openingTimes[random.nextInt(openingTimes.length)];
    pstmtRestaurant.setString(3, randomOpeningTime); // Öffnungszeit setzen
    pstmtRestaurant.setString(4, "Ort" + i); // Ort
    pstmtRestaurant.setInt(5, (1010 + random.nextInt(1220))); // Plz
    pstmtRestaurant.addBatch();
    if (i % 100 == 0 || i == 350) {
      int[] resultRestaurant = pstmtRestaurant.executeBatch(); // Batch ausführen
        pstmtRestaurant.clearBatch(); // Batch leeren für das nächste Set von Inserts
    }
}
con.commit();
} catch (SQLException e) {
  e.printStackTrace();
  try {
      if (con != null) {
          con.rollback(); // Im Fehlerfall Änderungen rückgängig machen
      }
  } catch (SQLException ex) {
      ex.printStackTrace();
  }
}

//Gericht
try {
  con.setAutoCommit(false);
  pstmtGericht = con.prepareStatement(insertSqlGericht);
  Random random = new Random();
    for (int i = 1; i <= 350; i++) {
     pstmtGericht.setString(1, "Anschrift" + i); // Anschrift
     for (int j = 1; j <= 10; j++) {
        pstmtGericht.setString(2, "R" + i + "GerichtName" + j); // Name
        pstmtGericht.setInt(3, (5 + random.nextInt(55))); // Anschrift
        pstmtGericht.addBatch();
        }
    if (i % 100 == 0 || i == 350) {
      int[] resultGericht = pstmtGericht.executeBatch(); // Batch ausführen
        pstmtGericht.clearBatch(); // Batch leeren für das nächste Set von Inserts
    }
}
con.commit();

} catch (SQLException e) {
  e.printStackTrace();
  try {
      if (con != null) {
          con.rollback(); // Im Fehlerfall Änderungen rückgängig machen
      }
  } catch (SQLException ex) {
      ex.printStackTrace();
  }
}

List<Integer> alleGerichtIds = new ArrayList<>();
try {
    Statement stmt = con.createStatement();
    ResultSet rs = stmt.executeQuery("SELECT GerichtID FROM Gericht");
    while (rs.next()) {
        alleGerichtIds.add(rs.getInt("GerichtID"));
    }
} catch (SQLException e) {
    e.printStackTrace();
}


//Kochen

try {
    con.setAutoCommit(false);
    pstmtKochen = con.prepareStatement(insertSqlKochen);

    for (int i = 1; i <= 350; i++) { // Für jedes Restaurant
        for (int j = 0; j < 10; j++) { // Wähle die ersten 35 Gerichte nach dem Mischen
            pstmtKochen.setInt(1, alleGerichtIds.get(j)); // Zufällige GerichtID
            pstmtKochen.setString(2, "Anschrift" + i); // Restaurant
    
            pstmtKochen.addBatch();
        }
        if (i % 100 == 0 || i == 350) {
          int[] resultKochen = pstmtKochen.executeBatch();
          pstmtKochen.clearBatch();
        }
    
    }
con.commit();

} catch (SQLException e) {
  e.printStackTrace();
  try {
      if (con != null) {
          con.rollback(); // Im Fehlerfall Änderungen rückgängig machen
      }
  } catch (SQLException ex) {
      ex.printStackTrace();
  }
}

//Lieferant
try {
  con.setAutoCommit(false);
  pstmtLieferrant = con.prepareStatement(insertSqlLieferrant);
  for (int i = 1; i <= 400; i++) {
    pstmtLieferrant.setInt(1, i); // LieferrantID
    pstmtLieferrant.setString(2, "Lieferant" + i); // Name
    String fahrzeugTyp = (i % 2 == 0) ? "A" : "F"; // Wechselt zwischen "Auto" und "Fahrrad"
    pstmtLieferrant.setString(3, fahrzeugTyp); // FahrzeugTyp
    pstmtLieferrant.addBatch();

    if (i % 100 == 0 || i == 400) {
      int[] resultLieferrant = pstmtLieferrant.executeBatch();
        pstmtLieferrant.clearBatch();
    }
}

con.commit();

} catch (SQLException e) {
  e.printStackTrace();
  try {
      if (con != null) {
          con.rollback(); // Im Fehlerfall Änderungen rückgängig machen
      }
  } catch (SQLException ex) {
      ex.printStackTrace();
  }
}

try {
  // Get Benutzer IDs
  Statement stmtBenutzer = con.createStatement();
  ResultSet rsBenutzer = stmtBenutzer.executeQuery("SELECT BenutzerID FROM Benutzer");
  while (rsBenutzer.next()) {
      benutzerIds.add(rsBenutzer.getInt("BenutzerID"));
  }

  // Get Restaurant Addresses and LiefernKosten
  Statement stmtRestaurant = con.createStatement();
  ResultSet rsRestaurant = stmtRestaurant.executeQuery("SELECT Anschrift FROM Restaurant");
  while (rsRestaurant.next()) {
      restaurantAnschrifts.add(rsRestaurant.getString("Anschrift"));
      // Assuming LiefernKosten is related to Restaurant and constant for simplicity
  }

  // Get Gericht IDs and Prices
  Statement stmtGericht = con.createStatement();
  ResultSet rsGericht = stmtGericht.executeQuery("SELECT GerichtID, Price FROM Gericht");
  while (rsGericht.next()) {
      gerichtIds.add(rsGericht.getInt("GerichtID"));
      gerichtPrices.add(rsGericht.getInt("Price"));
  }

  // Insert into Warenkorb and OrderItem
  pstmtWarenkorb = con.prepareStatement(
      "INSERT INTO Warenkorb (BenutzerID, ResturantAnschrift, LiefernKosten) VALUES(?, ?, ?)",
      Statement.RETURN_GENERATED_KEYS
  );
  pstmtOrderItem = con.prepareStatement(
      "INSERT INTO OrderItem (WarenkorbID, GerichtID, Price, Quantity, TotalPriceG) VALUES(?, ?, ?, ?, ?)"
  );

Map<Integer, Boolean> gratisLiefernMap = new HashMap<>();
try {
    Statement stmt = con.createStatement();
    ResultSet rs = stmt.executeQuery("SELECT BenutzerID, GratisLiefern FROM Benutzer");
    while (rs.next()) {
        int benutzerId = rs.getInt("BenutzerID");
        boolean gratisLiefern = rs.getInt("GratisLiefern") == 1; // Assuming GratisLiefern is stored as an integer (1 or 0)
        gratisLiefernMap.put(benutzerId, gratisLiefern);
    }
} catch (SQLException e) {
    e.printStackTrace();
}

Random randomGenerator = new Random();
  for (int i = 0; i <= 2000; i++) {

    int randomIndexB = randomGenerator.nextInt(benutzerIds.size());
    int randomBenutzerID = benutzerIds.get(randomIndexB);
    boolean isGratisLiefern = gratisLiefernMap.getOrDefault(randomBenutzerID, false);

    int randomIndexR = randomGenerator.nextInt(restaurantAnschrifts.size());
    String randomRestaurantAnschrift = restaurantAnschrifts.get(randomIndexR);

    pstmtWarenkorb.setInt(1, randomBenutzerID);
    pstmtWarenkorb.setString(2, randomRestaurantAnschrift);
    pstmtWarenkorb.setInt(3, isGratisLiefern ? 0 : 3);
    pstmtWarenkorb.executeUpdate();

       }
        con.commit();
      } catch (SQLException e) {
        e.printStackTrace();
        try {
            if (con != null) {
                con.rollback();
            }
        } catch (SQLException ex) {
            ex.printStackTrace();
        }
      }

try {
  // Get Benutzer IDs
  Statement stmtWarenkorb = con.createStatement();
  ResultSet rsWarenkorb = stmtWarenkorb.executeQuery("SELECT WarenkorbID FROM Warenkorb");
  while (rsWarenkorb.next()) {
      warenkorbIds.add(rsWarenkorb.getInt("WarenkorbID"));
    }
  } catch (SQLException e) {
       e.printStackTrace();
   }

Random randomGenerator = new Random();
try{
  for (int i = 0; i <= 3000; i++) {

        // Wählen Sie zufällig eine WarenkorbID aus
        int randomWarenkorbIndex = randomGenerator.nextInt(warenkorbIds.size());
        int warenkorbId = warenkorbIds.get(randomWarenkorbIndex);

        // Wählen Sie zufällig eine GerichtID aus
        int randomGerichtIndex = randomGenerator.nextInt(gerichtIds.size());
        int gerichtId = gerichtIds.get(randomGerichtIndex);

        // Wählen Sie zufällig einen Preis aus
        int price = gerichtPrices.get(randomGerichtIndex);

        // Zufällige Menge zwischen 1 und 5 generieren
        int quantity = 1 + randomGenerator.nextInt(5);
      pstmtOrderItem.setInt(1, warenkorbId);
      pstmtOrderItem.setInt(2, gerichtId);
      pstmtOrderItem.setInt(3, price);
      pstmtOrderItem.setInt(4, quantity);
      pstmtOrderItem.setInt(5, price * quantity); // TotalPriceG = Price * Quantity
      pstmtOrderItem.executeUpdate();

      }
} catch (SQLException e) {
    e.printStackTrace();
}


  } catch (Exception e) {
        System.err.println("Error while executing INSERT INTO statement: " + e.getMessage());
      }
      ResultSet rsBenutzer = pstmtBenutzer.executeQuery("SELECT COUNT(*) FROM Benutzer");
      if (rsBenutzer.next()) {
        int countBenutzer = rsBenutzer.getInt(1);
        System.out.println("Number of datasets Benuzter: " + countBenutzer);
      }

      ResultSet rsApp = stmtApp.executeQuery("SELECT COUNT(*) FROM App");
      if (rsApp.next()) {
          int countApp = rsApp.getInt(1);
          System.out.println("Number of datasets App: " + countApp);
      }

      ResultSet rsRestaurant = pstmtRestaurant.executeQuery("SELECT COUNT(*) FROM Restaurant");
      if (rsRestaurant.next()) {
          int countRestaurant = rsRestaurant.getInt(1);
          System.out.println("Number of datasets Restaurant: " + countRestaurant);
      }

      ResultSet rsGericht = pstmtGericht.executeQuery("SELECT COUNT(*) FROM Gericht");
      if (rsGericht.next()) {
          int countGericht = rsGericht.getInt(1);
          System.out.println("Number of datasets Gericht: " + countGericht);
      }

      ResultSet rsLieferrant = pstmtLieferrant.executeQuery("SELECT COUNT(*) FROM Lieferrant");
      if (rsLieferrant.next()) {
          int countLieferrant = rsLieferrant.getInt(1);
          System.out.println("Number of datasets Lieferrant: " + countLieferrant);
      }

      ResultSet rsKochen = pstmtKochen.executeQuery("SELECT COUNT(*) FROM Kochen");
      if (rsKochen.next()) {
          int countKochen = rsKochen.getInt(1);
          System.out.println("Number of datasets Kochen: " + countKochen);
      }

            ResultSet rsWarenkorb = pstmtWarenkorb.executeQuery("SELECT COUNT(*) FROM Warenkorb");
            if (rsWarenkorb.next()) {
                int countWarenkorb = rsWarenkorb.getInt(1);
                System.out.println("Number of datasets Warenkorb: " + countWarenkorb);
            }

      ResultSet rsOrderItem = pstmtOrderItem.executeQuery("SELECT COUNT(*) FROM OrderItem");
      if (rsOrderItem.next()) {
          int countOrderItem = rsOrderItem.getInt(1);
          System.out.println("Number of datasets OrderItem: " + countOrderItem);
      }

      
      rsBenutzer.close();
      rsApp.close();
      rsLieferrant.close();
      rsRestaurant.close();
      pstmtBenutzer.close();
      pstmtRestaurant.close();
      pstmtGericht.close();
      pstmtLieferrant.close();
      pstmtKochen.close();
      stmtApp.close();
      con.close();
    } catch (Exception e) {
      System.err.println(e.getMessage());
    }
  }
}