from flask import Flask, request, jsonify, session, redirect, render_template
import segno, base64
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
# QR Generation API (MICRO QR)
# ---------------------------
@app.route("/add-item", methods=["POST"])
def add_item():
    if "user" not in session:
        return jsonify({"error": "Not logged in"})

    data = request.json or request.form

    # Load database
    with open("product_data.json", "r") as f:
        product_store = json.load(f)

    # Generate unique product code
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    # Read input fields
    item_id = data.get("id")
    name = data.get("name")
    price = data.get("price")
    mfg_date = data.get("mfg_date")
    expiry_date = data.get("expiry_date")
    authenticity = data.get("authenticity")
    brand = data.get("brand")

    # Store the product
    product_store[code] = {
        "id": item_id,
        "name": name,
        "price": price,
        "mfg_date": mfg_date,
        "expiry": expiry_date,
        "authenticity": authenticity,
        "brand": brand
    }

    with open("product_data.json", "w") as f:
        json.dump(product_store, f, indent=4)

    # Your live Render domain
    host = "https://smart-qr-4.onrender.com"
    full_url = f"{host}/view-item?code={code}"

    print("\nMicro QR URL:", full_url, "\n")

    # MICRO QR generation using segno
    qr = segno.make(code, micro=True)   # only the 6-digit code
    buffer = BytesIO()
    qr.save(buffer, kind='png', scale=5)
    buffer.seek(0)
    qr_base64 = base64.b64encode(buffer.read()).decode("utf-8")


    return jsonify({
        "message": "Micro QR Generated Successfully!",
        "qr_base64": qr_base64
    })


# ---------------------------
# PRODUCT VIEW PAGE (opens from QR)
# ---------------------------
@app.route("/view-item")
def view_item():
    # 1. Try ?code=XYZ (normal case)
    code = request.args.get("code")

    # 2. If scanner gives only the code (like TJ5LXE)
    if not code:
        raw = request.full_path.strip("/?")
        code = raw.replace("/", "").replace("?", "").strip()

    # Clean extra characters
    code = code.strip().replace("\n", "").replace("\r", "")

    # Load product database
    with open("product_data.json", "r") as f:
        product_store = json.load(f)

    # Validate product code
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
        authenticity=item["authenticity"],
        brand=item["brand"]
    )




# ---------------------------
# RUN FLASK SERVER
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True, port=8080, use_reloader=False)
