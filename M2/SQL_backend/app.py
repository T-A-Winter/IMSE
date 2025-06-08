from flask import Flask, request, jsonify
from SQL_backend.db import SessionLocal, engine
from SQL_backend.models import User
from sqlalchemy.exc import IntegrityError
from SQL_backend.db import Base

app = Flask(__name__)
Base.metadata.create_all(bind=engine)

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()

    if not all(k in data for k in ("first_name", "last_name", "email", "password")):
        return jsonify({"error": "Missing required fields"}), 400

    new_user = User(
        first_name=data["first_name"],
        last_name=data["last_name"],
        email=data["email"],
        city=data.get("city"),
        street=data.get("street"),
        zipcode=data.get("zipcode"),
    )
    new_user.set_password(data["password"])

    session = SessionLocal()
    try:
        session.add(new_user)
        session.commit()
        return jsonify({"message": "User created successfully"}), 201
    except IntegrityError:
        session.rollback()
        return jsonify({"error": "Email already registered"}), 409
    finally:
        session.close()