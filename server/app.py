#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


# GET /restaurants
@app.route("/restaurants", methods=["GET"])
def get_restaurants():
    restaurants = Restaurant.query.all()
    result = [r.to_dict(only=("id", "name", "address")) for r in restaurants]
    return make_response(jsonify(result), 200)


# GET /restaurants/<int:id>
@app.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)
    return make_response(jsonify(restaurant.to_dict()), 200)


# DELETE /restaurants/<int:id>
@app.route("/restaurants/<int:id>", methods=["DELETE"])
def delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if not restaurant:
        return make_response(jsonify({"error": "Restaurant not found"}), 404)
    db.session.delete(restaurant)
    db.session.commit()
    return ("", 204)


# GET /pizzas
@app.route("/pizzas", methods=["GET"])
def get_pizzas():
    pizzas = Pizza.query.all()
    result = [p.to_dict(only=("id", "name", "ingredients")) for p in pizzas]
    return make_response(jsonify(result), 200)


# POST /restaurant_pizzas
@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()
    if not data:
        return make_response(jsonify({"errors": ["validation errors"]}), 400)

    price = data.get("price")
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")

    # Required fields
    if pizza_id is None or restaurant_id is None or price is None:
        return make_response(jsonify({"errors": ["validation errors"]}), 400)

    # Check referenced objects
    pizza = Pizza.query.get(pizza_id)
    restaurant = Restaurant.query.get(restaurant_id)
    if not pizza or not restaurant:
        return make_response(jsonify({"errors": ["validation errors"]}), 400)

    try:
        rp = RestaurantPizza(price=price, pizza=pizza, restaurant=restaurant)
        db.session.add(rp)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return make_response(jsonify({"errors": ["validation errors"]}), 400)

    return make_response(jsonify(rp.to_dict()), 201)


if __name__ == "__main__":
    app.run(port=5555, debug=True)
