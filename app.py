from flask import Flask, jsonify, request
import os
from models import db, Hero, Power, HeroPower
try:
    from flask_cors import CORS
except Exception:
    CORS = None

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "superheroes.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

CORS(app) if CORS else None
db.init_app(app)


# ---------------- HERO ROUTES ---------------- #

@app.route("/heroes", methods=["GET"])
def get_heroes():
    heroes = Hero.query.all()
    return jsonify([hero.to_dict() for hero in heroes]), 200


@app.route("/heroes/<int:id>", methods=["GET"])
def get_hero_by_id(id):
    hero = Hero.query.get(id)

    if not hero:
        return jsonify({"error": "Hero not found"}), 404

    return jsonify(hero.to_dict(include_powers=True)), 200


# ---------------- POWER ROUTES ---------------- #

@app.route("/powers", methods=["GET"])
def get_powers():
    powers = Power.query.all()
    return jsonify([power.to_dict() for power in powers]), 200


@app.route("/powers/<int:id>", methods=["GET"])
def get_power_by_id(id):
    power = Power.query.get(id)

    if not power:
        return jsonify({"error": "Power not found"}), 40

    return jsonify(power.to_dict()), 200


@app.route("/powers/<int:id>", methods=["PATCH"])
def update_power(id):
    power = Power.query.get(id)

    if not power:
        return jsonify({"error": "Power not found"}), 404

    data = request.get_json()
    description = data.get("description")

    try:
        power.description = description
        db.session.commit()
        return jsonify(power.to_dict()), 200
    except Exception:
        return jsonify({"errors": ["validation errors"]}), 422


# ---------------- HERO POWER ROUTES ---------------- #

@app.route("/hero_powers", methods=["POST"])
def create_hero_power():
    data = request.get_json()

    try:
        hero_power = HeroPower(
            strength=data["strength"],
            hero_id=data["hero_id"],
            power_id=data["power_id"]
        )

        db.session.add(hero_power)
        db.session.commit()

        return jsonify(hero_power.to_dict(include_power=True, include_hero=True)), 201

    except Exception:
        return jsonify({"errors": ["validation errors"]}), 422


if __name__ == "__main__":
    app.run(port=5555, debug=True)
