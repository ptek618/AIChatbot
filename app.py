from __future__ import annotations

import json
import os
import random
from dataclasses import dataclass
from typing import Dict, List

from flask import Flask, jsonify, redirect, render_template, request, session, url_for


DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "options.json")
DEFAULT_TOWN = "Marion, IL"


@dataclass
class Option:
    name: str
    category: str
    ownership: str


app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")


def load_data() -> Dict[str, List[Dict[str, str]]]:
    if not os.path.exists(DATA_FILE):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        seed_data = {
            "towns": {
                DEFAULT_TOWN: [
                    {"name": "Walt's", "category": "Sit Down", "ownership": "Locally Owned"},
                    {"name": "17th Street Bar & Grill", "category": "Sit Down", "ownership": "Locally Owned"},
                    {"name": "El Torito", "category": "Sit Down", "ownership": "Locally Owned"},
                    {"name": "Pookie's Beer, Burgers & Bocce", "category": "Sit Down", "ownership": "Locally Owned"},
                    {"name": "Culver's", "category": "Fast Food", "ownership": "Chain"},
                    {"name": "Chick-fil-A", "category": "Fast Food", "ownership": "Chain"},
                    {"name": "Taco Bell", "category": "Fast Food", "ownership": "Chain"},
                    {"name": "Taqueria Los Tres Caminos (Food Truck)", "category": "Food Truck", "ownership": "Locally Owned"},
                    {"name": "Smokehouse 155 Food Truck", "category": "Food Truck", "ownership": "Locally Owned"},
                ]
            }
        }
        with open(DATA_FILE, "w", encoding="utf-8") as handle:
            json.dump(seed_data, handle, indent=2)
    with open(DATA_FILE, "r", encoding="utf-8") as handle:
        return json.load(handle)


def save_data(data: Dict[str, List[Dict[str, str]]]) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)


def get_town_options(town: str) -> List[Dict[str, str]]:
    data = load_data()
    return data.get("towns", {}).get(town, [])


def require_admin() -> bool:
    return session.get("is_admin", False)


@app.route("/")
def index():
    data = load_data()
    towns = sorted(data.get("towns", {}).keys())
    return render_template("index.html", default_town=DEFAULT_TOWN, towns=towns)


@app.route("/api/towns")
def towns():
    data = load_data()
    return jsonify({"towns": sorted(data.get("towns", {}).keys())})


@app.route("/api/options")
def options():
    town = request.args.get("town", DEFAULT_TOWN)
    options_list = get_town_options(town)
    return jsonify({"town": town, "options": options_list})


@app.route("/api/spin", methods=["POST"])
def spin():
    payload = request.get_json(silent=True) or {}
    town = payload.get("town", DEFAULT_TOWN)
    category = payload.get("category", "All")
    ownership = payload.get("ownership", "All")

    options_list = get_town_options(town)
    filtered = [
        option
        for option in options_list
        if (category == "All" or option["category"] == category)
        and (ownership == "All" or option["ownership"] == ownership)
    ]

    if not filtered:
        return jsonify({"error": "No matches for those filters."}), 404

    chosen = random.choice(filtered)
    return jsonify({"result": chosen})


@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password", "")
        admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")
        if password == admin_password:
            session["is_admin"] = True
            return redirect(url_for("admin_panel"))
        return render_template("login.html", error="Invalid password")

    return render_template("login.html", error=None)


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("index"))


@app.route("/admin/panel")
def admin_panel():
    if not require_admin():
        return redirect(url_for("admin_login"))

    data = load_data()
    towns = sorted(data.get("towns", {}).keys())
    selected_town = request.args.get("town", DEFAULT_TOWN)
    options_list = data.get("towns", {}).get(selected_town, [])
    return render_template(
        "admin.html",
        towns=towns,
        selected_town=selected_town,
        options_list=options_list,
    )


@app.route("/admin/options", methods=["POST"])
def admin_options():
    if not require_admin():
        return redirect(url_for("admin_login"))

    data = load_data()
    town = request.form.get("town", DEFAULT_TOWN).strip()
    action = request.form.get("action")

    towns_data = data.setdefault("towns", {})
    towns_data.setdefault(town, [])

    if action == "add":
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "Sit Down")
        ownership = request.form.get("ownership", "Locally Owned")
        if name:
            towns_data[town].append(
                {"name": name, "category": category, "ownership": ownership}
            )
    elif action == "delete":
        index = int(request.form.get("index", "-1"))
        if 0 <= index < len(towns_data[town]):
            towns_data[town].pop(index)
    elif action == "update":
        index = int(request.form.get("index", "-1"))
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "Sit Down")
        ownership = request.form.get("ownership", "Locally Owned")
        if 0 <= index < len(towns_data[town]) and name:
            towns_data[town][index] = {
                "name": name,
                "category": category,
                "ownership": ownership,
            }

    save_data(data)
    return redirect(url_for("admin_panel", town=town))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
