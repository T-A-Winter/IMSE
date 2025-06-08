from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

app = Flask(__name__)

# SQLAlchemy DB config (pretend the DB exists at this URI)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@mariadb/dbname'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# User model
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100))
    street = db.Column(db.String(100))
    zipcode = db.Column(db.String(20))

# Route to create a user
@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json()

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 409

    user = User(
        first_name=data["first_name"],
        last_name=data["last_name"],
        password=data["password"],  # 🔒 In real apps: hash this!
        email=data["email"],
        city=data["city"],
        street=data["street"],
        zipcode=data["zipcode"]
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created successfully", "user_id": user.id}), 201

# Only for development
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)