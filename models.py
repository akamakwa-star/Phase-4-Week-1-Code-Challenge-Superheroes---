from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates

db = SQLAlchemy()


class Hero(db.Model):
    __tablename__ = "heroes"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    super_name = db.Column(db.String)

    hero_powers = db.relationship(
        "HeroPower",
        back_populates="hero",
        cascade="all, delete"
    )

    def to_dict(self, include_powers=False):
        data = {
            "id": self.id,
            "name": self.name,
            "super_name": self.super_name
        }

        if include_powers:
            data["hero_powers"] = [
                hp.to_dict(include_power=True) for hp in self.hero_powers
            ]

        return data


class Power(db.Model):
    __tablename__ = "powers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)

    hero_powers = db.relationship(
        "HeroPower",
        back_populates="power",
        cascade="all, delete"
    )

    @validates("description")
    def validate_description(self, key, description):
        if not description or len(description) < 20:
            raise ValueError("Description must be at least 20 characters")
        return description

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }


class HeroPower(db.Model):
    __tablename__ = "hero_powers"

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String)

    hero_id = db.Column(db.Integer, db.ForeignKey("heroes.id"))
    power_id = db.Column(db.Integer, db.ForeignKey("powers.id"))

    hero = db.relationship("Hero", back_populates="hero_powers")
    power = db.relationship("Power", back_populates="hero_powers")

    @validates("strength")
    def validate_strength(self, key, strength):
        if strength not in ["Strong", "Weak", "Average"]:
            raise ValueError("Invalid strength")
        return strength

    def to_dict(self, include_power=False):
        data = {
            "id": self.id,
            "hero_id": self.hero_id,
            "power_id": self.power_id,
            "strength": self.strength
        }

        if include_power:
            data["power"] = self.power.to_dict()

        data["hero"] = self.hero.to_dict()
        data["power"] = self.power.to_dict()

        return data
