from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests

BACKEND_URL = "http://localhost:8000"

app = Flask(__name__)

@app.route("/")
def index():
    # Pagination parameters
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 10))
    except Exception:
        page = 1
        per_page = 10
    offset = (page - 1) * per_page
    try:
        resp = requests.get(f"{BACKEND_URL}/pets", params={"limit": per_page, "offset": offset})
        data = resp.json()
        pets = data.get("items", [])
        total = data.get("total", 0)
    except Exception:
        pets = []
        total = 0
    total_pages = max(1, (total + per_page - 1) // per_page)
    return render_template(
        "index.html",
        pets=pets,
        page=page,
        per_page=per_page,
        total=total,
        total_pages=total_pages
    )

@app.route("/add", methods=["POST"])
def add_pet():
    name = request.form["name"]
    species = request.form["species"]
    age = int(request.form["age"])
    requests.post(f"{BACKEND_URL}/pets", json={"name": name, "species": species, "age": age})
    return redirect(url_for("index"))

@app.route("/edit/<int:pet_id>", methods=["GET", "POST"])
def edit_pet(pet_id):
    if request.method == "POST":
        name = request.form["name"]
        species = request.form["species"]
        age = int(request.form["age"])
        requests.put(f"{BACKEND_URL}/pets/{pet_id}", json={"name": name, "species": species, "age": age})
        return redirect(url_for("index"))
    else:
        resp = requests.get(f"{BACKEND_URL}/pets/{pet_id}")
        pet = resp.json()
        return render_template("edit.html", pet=pet)

@app.route("/delete/<int:pet_id>", methods=["POST"])
def delete_pet(pet_id):
    requests.delete(f"{BACKEND_URL}/pets/{pet_id}")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(port=5000, debug=True)
