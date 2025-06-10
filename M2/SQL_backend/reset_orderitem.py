from db import engine, Base
from models import OrderItem

# Drop and recreate the OrderItem table
if __name__ == "__main__":
    # Drop the OrderItem table if it exists
    OrderItem.__table__.drop(engine, checkfirst=True)
    
    # Create the OrderItem table with the updated schema
    OrderItem.__table__.create(engine)
    
    print("OrderItem table has been reset successfully.") 