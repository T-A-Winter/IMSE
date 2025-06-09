from flask import Flask, request, jsonify
from db import SessionLocal, engine
from models import User
from sqlalchemy.exc import IntegrityError
from db import Base

app = Flask(__name__)
Base.metadata.create_all(bind=engine)

@app.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()

    if not all(k in data for k in ("first_name", "last_name", "email", "password")):
        return jsonify({"error": "Missing required fields"}), 400
    
    if data["password"] != data["confirm_password"]:
        return jsonify({"error" : "Passwords do not math"}), 400

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

@app.route("/signin", methods=["POST"])
def signin():
    data = request.get_json()

    if not all(k in data for k in ("email", "password")):
        return jsonify({"error": "Missing email or password"}), 400

    session = SessionLocal()
    
    try:
        user = session.query(User).filter_by(email=data["email"]).first()
        if user is None:
            return jsonify({"error": "User not found"}), 404

        if not user.check_password(data["password"]):
            return jsonify({"error": "Incorrect password"}), 401

        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email
            }
        }), 200
    finally:
        session.close()