from flask import Flask, request, jsonify, session, redirect, render_template
import segno
import base64
from io import BytesIO
import json
import random
import string
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"


# ---------------------------
# LOGIN USERS
# ---------------------------
USERS = {
    "pfizer_admin": "Pfizer@123",
    "novartis_user": "Novartis@123",
    "roche_ops": "Roche@123",
    "sanofi_manager": "Sanofi@123",
    "gsk_lead": "GSK@123",
    "bayer_staff": "Bayer@123",
    "merck_hr": "Merck@123",
    "astrazeneca_lab": "Astra@123",
    "lilly_exec": "Lilly@123",
    "cipla_team": "Cipla@123"
}


# ---------------------------
# LOGIN PAGE
# ---------------------------
@app.route("/")
def login_page():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    if username in USERS and USERS[username] == password:
        session["user"] = username
        return redirect("/generate-qr")

    return "Invalid Credentials"


# ---------------------------
# QR FORM PAGE
# ---------------------------
@app.route("/generate-qr")
def generate_page():
    if "user" not in session:
        return redirect("/")
    return render_template("qr_form.html")


# ---------------------------
# QR GENERATION (MICRO QR)
# ---------------------------
@app.route("/add-item", methods=["POST"])
def add_item():

    if "user" not in session:
        return jsonify({"error": "Not logged in"})

    data = request.json or request.form

    # Load product database
    with open("product_data.json", "r") as f:
        product_store = json.load(f)

    # Generate unique product code
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    # Save product details
    product_store[code] = {
        "id": data.get("id"),
        "name": data.get("name"),
        "price": data.get("price"),
        "mfg_date": data.get("mfg_date"),
        "expiry": data.get("expiry_date"),
        "brand": data.get("brand")
    }

    with open("product_data.json", "w") as f:
        json.dump(product_store, f, indent=4)

    # Micro QR only encodes the code
    micro_qr = segno.make(code, micro=True)

    buffer = BytesIO()
    micro_qr.save(buffer, kind='png', scale=15)

    buffer.seek(0)
    qr_base64 = base64.b64encode(buffer.read()).decode("utf-8")

    print("\nMICRO QR CODE:", code)
    print("Product URL:", f"https://smart-qr-4.onrender.com/view-item?code={code}\n")

    return jsonify({
        "message": "QR Generated Successfully!",
        "qr_base64": qr_base64
    })


# ---------------------------
# PRODUCT VIEW PAGE (SCAN RESULT)
# ---------------------------
@app.route("/view-item")
def view_item():

    # Case 1 — Normal URL: ?code=ABC123
    code = request.args.get("code")

    # Case 2 — Scanner gives only raw code
    if not code:
        raw = request.full_path.strip("/?")
        code = raw.replace("/", "").replace("?", "").strip()

    code = code.strip()

    # Load product database
    with open("product_data.json", "r") as f:
        product_store = json.load(f)

    if code not in product_store:
        return "Invalid or Expired QR Code"

    item = product_store[code]

    return render_template(
        "item_view.html",
        item_id=item["id"],
        name=item["name"],
        price=item["price"],
        mfg_date=item["mfg_date"],
        expiry=item["expiry"],
        brand=item["brand"]
    )


# ---------------------------
# RUN SERVER
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True, port=8080, use_reloader=False)
