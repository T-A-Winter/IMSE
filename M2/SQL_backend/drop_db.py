from SQL_backend.db import Base, engine

if __name__ == "__main__":
    print("Dropping all tables...")
    Base.metadata.drop_all(bind=engine)
    print("Done.")