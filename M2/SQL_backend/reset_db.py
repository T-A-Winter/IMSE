from SQL_backend.db import Base, engine

if __name__ == "__main__":
    print("Resetting database...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("Reset complete.")