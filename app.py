from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'superheroes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class HeroPower(db.Model):
    __tablename__ = 'hero_powers'
    id = db.Column(db.Integer, primary_key=True)
    hero_id = db.Column(db.Integer, db.ForeignKey('heroes.id'), nullable=False)
    power_id = db.Column(db.Integer, db.ForeignKey('powers.id'), nullable=False)
    strength = db.Column(db.String, nullable=False)

    hero = db.relationship('Hero', back_populates='hero_powers')
    power = db.relationship('Power', back_populates='hero_powers')

    @validates('strength')
    def validate_strength(self, key, value):
        allowed = {'Strong', 'Weak', 'Average'}
        if value not in allowed:
            raise ValueError(f"strength must be one of {sorted(allowed)}")
        return value

    def to_dict(self):
        return {
            'id': self.id,
            'hero_id': self.hero_id,
            'power_id': self.power_id,
            'strength': self.strength,
            'power': self.power.to_dict() if self.power else None
        }


class Hero(db.Model):
    __tablename__ = 'heroes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    super_name = db.Column(db.String, nullable=False)

    hero_powers = db.relationship('HeroPower', back_populates='hero', cascade='all, delete')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'super_name': self.super_name
        }


class Power(db.Model):
    __tablename__ = 'powers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)

    hero_powers = db.relationship('HeroPower', back_populates='power', cascade='all, delete')

    @validates('description')
    def validate_description(self, key, value):
        if not value or len(value.strip()) < 20:
            raise ValueError('description must be at least 20 characters long')
        return value

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description
        }


@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    return jsonify([h.to_dict() for h in heroes])


@app.route('/heroes/<int:hero_id>', methods=['GET'])
def get_hero(hero_id):
    hero = Hero.query.get(hero_id)
    if not hero:
        return jsonify({'error': 'Hero not found'}), 404

    data = hero.to_dict()
    data['hero_powers'] = [hp.to_dict() for hp in hero.hero_powers]
    return jsonify(data)


@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    return jsonify([p.to_dict() for p in powers])


@app.route('/powers/<int:power_id>', methods=['GET'])
def get_power(power_id):
    p = Power.query.get(power_id)
    if not p:
        return jsonify({'error': 'Power not found'}), 404
    return jsonify(p.to_dict())


@app.route('/powers/<int:power_id>', methods=['PATCH'])
def patch_power(power_id):
    p = Power.query.get(power_id)
    if not p:
        return jsonify({'error': 'Power not found'}), 404

    data = request.get_json() or {}
    description = data.get('description')
    if description is None:
        return jsonify({'errors': ['description is required']}), 400
    try:
        p.description = description
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # validation errors from model raise ValueError
        msg = str(e)
        return jsonify({'errors': [msg]}), 400
    return jsonify(p.to_dict())


@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json() or {}
    strength = data.get('strength')
    power_id = data.get('power_id')
    hero_id = data.get('hero_id')

    errors = []
    if strength not in {'Strong', 'Weak', 'Average'}:
        errors.append('strength must be one of Strong, Weak, Average')
    if not isinstance(power_id, int):
        errors.append('power_id must be provided')
    if not isinstance(hero_id, int):
        errors.append('hero_id must be provided')

    if errors:
        return jsonify({'errors': errors}), 400

    power = Power.query.get(power_id)
    hero = Hero.query.get(hero_id)
    if not power:
        return jsonify({'errors': ['power not found']}), 400
    if not hero:
        return jsonify({'errors': ['hero not found']}), 400

    try:
        hp = HeroPower(strength=strength, power=power, hero=hero)
        db.session.add(hp)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'errors': [str(e)]}), 400

    result = hp.to_dict()
    result['hero'] = hero.to_dict()
    result['power'] = power.to_dict()
    return jsonify(result), 201


if __name__ == '__main__':
    app.run(debug=True)
