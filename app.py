from flask import Flask, request, jsonify, session, redirect, render_template
import qrcode, base64
from io import BytesIO
import json, random, string

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------------------------
# 10 Pharma Login Credentials
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
# Login Page
# ---------------------------
@app.route("/")
def login_page():
    return render_template("login.html")


# ---------------------------
# Login Authentication
# ---------------------------
@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    if username in USERS and USERS[username] == password:
        session["user"] = username
        return redirect("/generate-qr")

    return "Invalid Credentials"


# ---------------------------
# QR Form Page (Protected)
# ---------------------------
@app.route("/generate-qr")
def generate_page():
    if "user" not in session:
        return redirect("/")
    return render_template("qr_form.html")


# ---------------------------
# QR GENERATION (PROFESSIONAL MODE)
# ---------------------------
@app.route("/add-item", methods=["POST"])
def add_item():
    if "user" not in session:
        return jsonify({"error": "Not logged in"})

    data = request.json or request.form

    # Load existing data
    with open("product_data.json", "r") as f:
        product_store = json.load(f)

    # Generate unique 6-character product code
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    # Save product details
    product_store[code] = {
        "id": data.get("id"),
        "name": data.get("name"),
        "price": data.get("price"),
        "expiry": data.get("expiry_date"),
        "authenticity": data.get("authenticity"),
        "brand": data.get("brand")
    }

    with open("product_data.json", "w") as f:
        json.dump(product_store, f, indent=4)

    # ---------------------------
    # ⭐ DYNAMIC HOST URL (works locally + works ON Render)
    # ---------------------------
    host = "https://smart-qr-4.onrender.com" # auto-detects domain
    full_url = f"{host}/view-item?code={code}"

    print("\nQR Link:", full_url, "\n")

    # Generate QR code
    img = qrcode.make(full_url)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    qr_base64 = base64.b64encode(buffer.read()).decode("utf-8")

    return jsonify({
        "message": "QR Generated Successfully!",
        "qr_base64": qr_base64
    })


# ---------------------------
# PRODUCT VIEW PAGE (opens from QR)
# ---------------------------
@app.route("/view-item")
def view_item():
    code = request.args.get("code")

    # Load product data
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
        expiry=item["expiry"],
        authenticity=item["authenticity"],
        brand=item["brand"]
    )


# ---------------------------
# RUN FLASK SERVER
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True, port=8080, use_reloader=False)
