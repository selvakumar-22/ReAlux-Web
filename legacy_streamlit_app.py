from flask import (
    Flask, request, redirect, url_for, session,
    render_template_string, send_file
)
import sqlite3
import io
import os
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from werkzeug.security import generate_password_hash, check_password_hash

# ============================================================
# ReAlux - AI Powered Aluminium Dross Recovery Prediction
# Flask prototype for VS Code
# ============================================================

app = Flask(__name__)
app.secret_key = os.environ.get("REALUX_SECRET_KEY", "change-this-secret-key")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE_DIR, "realux.db")

FEATURES = [
    "metal_pct", "oxide_pct", "salt_pct",
    "Al", "Fe", "Mg", "Si", "Cu", "Zn",
    "Ni", "Mn", "Ti", "Ca", "Na", "K", "Cl"
]

UPLOAD_FOLDER = os.path.join(BASE_DIR, "data")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ============================================================
# DATABASE
# ============================================================

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            sample_name TEXT,
            metal_pct REAL,
            oxide_pct REAL,
            salt_pct REAL,
            metal_recovery REAL,
            alumina_recovery REAL,
            category TEXT,
            route TEXT,
            furnace TEXT,
            temperature TEXT,
            hydro_ph TEXT,
            leaching_time TEXT,
            application TEXT,
            environmental_score REAL,
            economic_score REAL,
            confidence_score REAL,
            reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
# DEMO ML MODEL
# IMPORTANT:
# This is synthetic demonstration data.
# Replace with a real experimentally validated dataset/model
# before using predictions for industrial decisions.
# ============================================================

def train_demo_models():
    rng = np.random.default_rng(42)

    X = rng.uniform(0, 100, (1000, 16))

    metal_recovery = (
        0.78 * X[:, 0]
        - 0.12 * X[:, 1]
        - 0.05 * X[:, 2]
        + 0.03 * X[:, 3]
        - 0.02 * X[:, 4]
        + rng.normal(0, 3, 1000)
    )

    alumina_recovery = (
        0.62 * X[:, 1]
        - 0.08 * X[:, 0]
        + 0.02 * X[:, 5]
        + rng.normal(0, 2.5, 1000)
    )

    metal_model = LinearRegression()
    alumina_model = LinearRegression()

    metal_model.fit(X, metal_recovery)
    alumina_model.fit(X, alumina_recovery)

    return metal_model, alumina_model


metal_model, alumina_model = train_demo_models()


# ============================================================
# STYLE
# ============================================================

STYLE = """
<style>
:root{
    --navy:#123b5d;
    --green:#087f5b;
    --light:#f4f8fb;
    --border:#d8e1e8;
    --orange:#e68a00;
    --red:#d62828;
}

*{box-sizing:border-box;}

body{
    margin:0;
    font-family:Arial, Helvetica, sans-serif;
    background:var(--light);
    color:#172b3a;
}

.container{
    width:92%;
    max-width:1180px;
    margin:30px auto;
}

.nav{
    background:white;
    border-bottom:1px solid var(--border);
    padding:16px 4%;
    display:flex;
    justify-content:space-between;
    align-items:center;
}

.logo{
    font-size:28px;
    font-weight:800;
    color:var(--green);
}

.nav a{
    margin-left:18px;
    color:var(--navy);
    text-decoration:none;
    font-weight:700;
}

.card{
    background:white;
    padding:28px;
    border-radius:16px;
    box-shadow:0 5px 22px rgba(20,50,70,.08);
    margin-bottom:22px;
    border:1px solid #edf1f4;
}

.hero{
    text-align:center;
    padding:55px 30px;
}

h1,h2,h3{
    color:var(--navy);
}

.hero h1{
    font-size:42px;
    margin:10px 0;
}

.subtitle{
    font-size:18px;
    color:#607483;
}

.grid{
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:18px;
}

.grid-2{
    display:grid;
    grid-template-columns:repeat(2,1fr);
    gap:18px;
}

.box{
    padding:22px;
    background:#f7fbfd;
    border:1px solid var(--border);
    border-radius:13px;
}

.metric{
    font-size:32px;
    font-weight:800;
    color:var(--green);
}

.high{color:#008000;}
.medium{color:var(--orange);}
.low{color:var(--red);}

button,.btn{
    display:inline-block;
    background:var(--green);
    color:white;
    border:none;
    padding:12px 20px;
    border-radius:8px;
    cursor:pointer;
    font-weight:700;
    text-decoration:none;
    margin:4px;
}

button:hover,.btn:hover{
    background:#056647;
}

.btn-secondary{
    background:var(--navy);
}

.btn-orange{
    background:var(--orange);
}

input,select{
    width:100%;
    padding:12px;
    margin:7px 0 16px;
    border:1px solid #ccd6df;
    border-radius:8px;
    background:white;
}

label{
    font-weight:700;
    color:#334e60;
}

.notice{
    padding:14px 18px;
    border-radius:10px;
    background:#fff8e8;
    border:1px solid #f0d38a;
    color:#6d5100;
    margin-bottom:18px;
}

.success{
    padding:14px 18px;
    border-radius:10px;
    background:#edf9f3;
    border:1px solid #a9dec4;
    color:#12643f;
}

.error{
    padding:14px 18px;
    border-radius:10px;
    background:#fff0f0;
    border:1px solid #efb3b3;
    color:#8d2020;
}

table{
    width:100%;
    border-collapse:collapse;
}

th,td{
    padding:11px;
    border-bottom:1px solid #e5ebef;
    text-align:left;
    font-size:14px;
}

th{
    background:#123b5d;
    color:white;
}

.small{
    color:#6b7e8c;
    font-size:13px;
}

.badge{
    display:inline-block;
    padding:6px 10px;
    border-radius:20px;
    font-weight:700;
    font-size:13px;
    background:#eaf4ef;
    color:#087f5b;
}

.footer{
    text-align:center;
    padding:30px;
    color:#718391;
}

@media(max-width:850px){
    .grid,.grid-2{
        grid-template-columns:1fr;
    }
    .hero h1{
        font-size:30px;
    }
}
</style>
"""


# ============================================================
# HELPERS
# ============================================================

def page(body, **context):
    email = session.get("email")
    nav = f"""
    <div class="nav">
        <div class="logo">ReAlux</div>
        <div>
            <a href="{url_for('home')}">Home</a>
            {"<a href='/dashboard'>Dashboard</a><a href='/history'>History</a><a href='/logout'>Logout</a>" if email else ""}
        </div>
    </div>
    """
    return render_template_string(
        STYLE + nav + '<div class="container">' + body + '</div>'
        '<div class="footer">ReAlux • Turning Dross into Value</div>',
        **context
    )


def require_login():
    return "email" not in session


def clamp(value, low=0, high=100):
    return float(max(low, min(high, value)))


def classify_recovery(metal_recovery):
    if metal_recovery < 40:
        return "Low Recovery", "low"
    elif metal_recovery <= 70:
        return "Medium Recovery", "medium"
    return "High Recovery", "high"


def recommend_process(data, metal_recovery, alumina_recovery):
    metal = float(data["metal_pct"])
    oxide = float(data["oxide_pct"])
    salt = float(data["salt_pct"])

    if metal >= 70:
        route = "Pyrometallurgical Recovery"
        furnace = "Rotary / Reverberatory Furnace"
        temperature = "700–900 °C*"
        hydro_ph = "Not primary route"
        leaching_time = "Not primary route"
        application = "Secondary Aluminium / Casting Alloys"
        reason = (
            "The sample has a high metallic aluminium fraction, so "
            "thermal separation and metal recovery are the primary opportunity."
        )
    elif oxide >= 40:
        route = "Hydrometallurgical Recovery"
        furnace = "Not primary route"
        temperature = "Not primary route"
        hydro_ph = "Process-validated pH range required"
        leaching_time = "Process-validated time required"
        application = "Alumina / Ceramic / Mineral Applications"
        reason = (
            "The relatively high oxide fraction indicates greater potential "
            "for alumina-rich residue recovery and chemical processing."
        )
    elif salt >= 20:
        route = "Hybrid Recovery + Salt Processing"
        furnace = "Rotary / Controlled Thermal Unit"
        temperature = "Process-dependent"
        hydro_ph = "Process-dependent"
        leaching_time = "Process-dependent"
        application = "Secondary Aluminium + Salt Recovery"
        reason = (
            "The composition contains significant salt and mixed phases, "
            "so metal recovery can be combined with residue and salt processing."
        )
    else:
        route = "Hybrid Recovery"
        furnace = "Rotary / Controlled Furnace"
        temperature = "Process-dependent"
        hydro_ph = "Process-dependent"
        leaching_time = "Process-dependent"
        application = "Cement / Ceramics / Industrial Materials"
        reason = (
            "The composition is mixed, so a combined recovery and residue "
            "utilization pathway is suggested."
        )

    return {
        "route": route,
        "furnace": furnace,
        "temperature": temperature,
        "hydro_ph": hydro_ph,
        "leaching_time": leaching_time,
        "application": application,
        "reason": reason
    }


def predict_data(data, sample_name="Manual Sample"):
    values = np.array(
        [float(data[x]) for x in FEATURES],
        dtype=float
    ).reshape(1, -1)

    metal_prediction = clamp(metal_model.predict(values)[0])
    alumina_prediction = clamp(alumina_model.predict(values)[0])

    category, css_class = classify_recovery(metal_prediction)
    recommendation = recommend_process(
        data, metal_prediction, alumina_prediction
    )

    # Prototype confidence score. In a research version, calculate this
    # from a validated model, calibration, uncertainty estimation, etc.
    confidence = clamp(
        55
        + abs(metal_prediction - 50) * 0.35
        + abs(alumina_prediction - 30) * 0.15
    )

    environmental_score = clamp(
        60 + (100 - float(data["salt_pct"])) * 0.25
    )

    economic_score = clamp(
        45
        + metal_prediction * 0.40
        + alumina_prediction * 0.10
    )

    return {
        "sample_name": sample_name,
        "metal_recovery": metal_prediction,
        "alumina_recovery": alumina_prediction,
        "category": category,
        "css_class": css_class,
        "confidence": confidence,
        "environmental_score": environmental_score,
        "economic_score": economic_score,
        **recommendation
    }


def save_analysis(result, data):
    if "email" not in session:
        return

    conn = get_db()
    conn.execute("""
        INSERT INTO analyses (
            email, sample_name, metal_pct, oxide_pct, salt_pct,
            metal_recovery, alumina_recovery, category, route,
            furnace, temperature, hydro_ph, leaching_time,
            application, environmental_score, economic_score,
            confidence_score, reason
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session["email"],
        result["sample_name"],
        float(data["metal_pct"]),
        float(data["oxide_pct"]),
        float(data["salt_pct"]),
        result["metal_recovery"],
        result["alumina_recovery"],
        result["category"],
        result["route"],
        result["furnace"],
        result["temperature"],
        result["hydro_ph"],
        result["leaching_time"],
        result["application"],
        result["environmental_score"],
        result["economic_score"],
        result["confidence"],
        result["reason"]
    ))
    conn.commit()
    conn.close()


def parse_uploaded_file(file_storage):
    filename = file_storage.filename.lower()

    if filename.endswith(".csv"):
        df = pd.read_csv(file_storage)
    elif filename.endswith(".xlsx") or filename.endswith(".xls"):
        df = pd.read_excel(file_storage)
    else:
        raise ValueError("Please upload CSV or Excel file.")

    missing = [x for x in FEATURES if x not in df.columns]

    if missing:
        raise ValueError(
            "Missing required columns: " + ", ".join(missing)
        )

    return df


def row_to_data(row):
    data = {}
    for feature in FEATURES:
        value = pd.to_numeric(row[feature], errors="coerce")
        if pd.isna(value):
            raise ValueError(f"Invalid or missing value for {feature}.")
        data[feature] = float(value)

    data["dross_type"] = row.get("dross_type", "Unknown")
    data["xrd"] = row.get("xrd", "Not provided")
    data["sem"] = row.get("sem", "Not provided")
    return data


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():
    return page("""
    <div class="card hero">
        <div class="logo">ReAlux</div>
        <h1>AI Powered Aluminium Dross<br>
        Recovery Prediction & Recommendation System</h1>

        <p class="subtitle">
            Turning Aluminium Dross into Value using Artificial Intelligence
        </p>

        <br>

        <a class="btn" href="/login">Login</a>
        <a class="btn btn-secondary" href="/register">Create Account</a>

        <div class="notice" style="margin-top:30px;text-align:left;">
            <b>Prototype notice:</b>
            The included ML model uses synthetic demonstration data.
            Replace it with experimentally validated aluminium-dross data
            before using the system for industrial decisions.
        </div>
    </div>

    <div class="grid">
        <div class="box">
            <h3>AI Prediction</h3>
            <p>Estimate metal and alumina recovery.</p>
        </div>
        <div class="box">
            <h3>Smart Recommendation</h3>
            <p>Suggest a suitable recovery pathway.</p>
        </div>
        <div class="box">
            <h3>Waste → Value</h3>
            <p>Connect recovered materials with possible applications.</p>
        </div>
    </div>
    """)


# ============================================================
# REGISTER
# ============================================================

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            error = "Email and password are required."
        elif len(password) < 6:
            error = "Password must contain at least 6 characters."
        else:
            conn = get_db()
            try:
                conn.execute(
                    "INSERT INTO users(email,password_hash) VALUES(?,?)",
                    (email, generate_password_hash(password))
                )
                conn.commit()
                conn.close()
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                conn.close()
                error = "Email is already registered."

    return page("""
    <div class="card" style="max-width:520px;margin:50px auto;">
        <h1>Create ReAlux Account</h1>

        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}

        <form method="POST">
            <label>Email</label>
            <input type="email" name="email" required>

            <label>Create Password</label>
            <input type="password" name="password" minlength="6" required>

            <button type="submit">Create Account</button>
        </form>

        <p><a href="/login">Already have an account?</a></p>
    </div>
    """, error=error)


# ============================================================
# LOGIN
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE email=?",
            (email,)
        ).fetchone()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session["email"] = email
            return redirect(url_for("input_method"))

        error = "Invalid email or password."

    return page("""
    <div class="card" style="max-width:520px;margin:50px auto;">
        <h1>ReAlux Login</h1>

        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}

        <form method="POST">
            <label>Email</label>
            <input type="email" name="email" required>

            <label>Password</label>
            <input type="password" name="password" required>

            <button type="submit">Login</button>
        </form>

        <p><a href="/register">Create New Account</a></p>
    </div>
    """, error=error)


# ============================================================
# INPUT METHOD
# ============================================================

@app.route("/input-method")
def input_method():
    if require_login():
        return redirect(url_for("login"))

    return page("""
    <div class="card">
        <h1>How do you want to provide Dross Data?</h1>
        <p class="subtitle">
            Select Manual, File, or Both.
        </p>

        <div class="grid">
            <div class="box">
                <h2>Manual Input</h2>
                <p>Enter composition values directly.</p>
                <a class="btn" href="/manual">Choose Manual</a>
            </div>

            <div class="box">
                <h2>File Upload</h2>
                <p>Upload CSV or Excel data.</p>
                <a class="btn" href="/file">Choose File</a>
            </div>

            <div class="box">
                <h2>Both</h2>
                <p>Upload a sample and then edit its values.</p>
                <a class="btn" href="/both">Choose Both</a>
            </div>
        </div>
    </div>
    """)


# ============================================================
# MANUAL INPUT
# ============================================================

@app.route("/manual")
def manual():
    if require_login():
        return redirect(url_for("login"))

    return page("""
    <div class="card">
        <h1>Manual Dross Sample Input</h1>
        <p class="small">
            Enter the measured composition of the aluminium dross sample.
        </p>

        <form action="/predict" method="POST">
            <label>Sample Name</label>
            <input name="sample_name" value="REALUX-001">

            <div class="grid">
                {% for f in features %}
                <div>
                    <label>{{ labels[f] }}</label>
                    <input name="{{ f }}" value="{{ defaults[f] }}"
                           type="number" step="any" required>
                </div>
                {% endfor %}
            </div>

            <div class="grid-2">
                <div>
                    <label>Dross Type</label>
                    <select name="dross_type">
                        <option>White Dross</option>
                        <option>Black Dross</option>
                        <option>Salt Slag</option>
                    </select>
                </div>

                <div>
                    <label>XRD Phase</label>
                    <input name="xrd" value="Alpha Alumina">
                </div>

                <div>
                    <label>SEM Morphology</label>
                    <input name="sem" value="Fine Particle">
                </div>
            </div>

            <button type="submit">Analyze with AI</button>
            <a class="btn btn-secondary" href="/input-method">Back</a>
        </form>
    </div>
    """,
    features=FEATURES,
    labels={
        "metal_pct": "Metal %",
        "oxide_pct": "Oxide %",
        "salt_pct": "Salt %",
        "Al": "Al %",
        "Fe": "Fe %",
        "Mg": "Mg %",
        "Si": "Si %",
        "Cu": "Cu %",
        "Zn": "Zn %",
        "Ni": "Ni %",
        "Mn": "Mn %",
        "Ti": "Ti %",
        "Ca": "Ca %",
        "Na": "Na %",
        "K": "K %",
        "Cl": "Cl %"
    },
    defaults={
        "metal_pct": 72,
        "oxide_pct": 15,
        "salt_pct": 10,
        "Al": 72,
        "Fe": 2,
        "Mg": 1,
        "Si": 5,
        "Cu": 0.5,
        "Zn": 0.4,
        "Ni": 0.1,
        "Mn": 0.2,
        "Ti": 0.1,
        "Ca": 0.3,
        "Na": 0.5,
        "K": 0.2,
        "Cl": 1
    })


# ============================================================
# FILE UPLOAD
# ============================================================

@app.route("/file", methods=["GET", "POST"])
def file_upload():
    if require_login():
        return redirect(url_for("login"))

    error = None

    if request.method == "POST":
        uploaded = request.files.get("file")

        if not uploaded or not uploaded.filename:
            error = "Please select a CSV or Excel file."
        else:
            try:
                df = parse_uploaded_file(uploaded)

                # Save uploaded copy
                safe_name = os.path.basename(uploaded.filename)
                save_path = os.path.join(UPLOAD_FOLDER, safe_name)
                uploaded.seek(0)
                uploaded.save(save_path)

                # Analyze first row
                data = row_to_data(df.iloc[0])
                result = predict_data(
                    data,
                    sample_name=str(
                        df.iloc[0].get("sample_name", "Uploaded Sample")
                    )
                )
                save_analysis(result, data)

                return render_result(result, data)

            except Exception as exc:
                error = str(exc)

    return page("""
    <div class="card">
        <h1>Upload Dross Dataset</h1>

        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}

        <form method="POST" enctype="multipart/form-data">
            <label>CSV / Excel File</label>
            <input type="file" name="file"
                   accept=".csv,.xlsx,.xls" required>

            <button type="submit">Upload & Analyze</button>
        </form>

        <div class="notice">
            <b>Required columns:</b><br>
            {{ required }}
        </div>
    </div>
    """,
    error=error,
    required=", ".join(FEATURES))


# ============================================================
# BOTH: FILE + MANUAL EDIT
# ============================================================

@app.route("/both", methods=["GET", "POST"])
def both():
    if require_login():
        return redirect(url_for("login"))

    error = None
    uploaded_data = None

    if request.method == "POST":
        if request.files.get("file") and request.files["file"].filename:
            try:
                df = parse_uploaded_file(request.files["file"])
                uploaded_data = row_to_data(df.iloc[0])
                uploaded_data["sample_name"] = str(
                    df.iloc[0].get("sample_name", "Uploaded Sample")
                )
            except Exception as exc:
                error = str(exc)

        elif request.form.get("loaded") == "1":
            try:
                data = {
                    f: float(request.form[f]) for f in FEATURES
                }
                data["dross_type"] = request.form.get("dross_type")
                data["xrd"] = request.form.get("xrd")
                data["sem"] = request.form.get("sem")

                result = predict_data(
                    data,
                    request.form.get("sample_name", "Both Input Sample")
                )
                save_analysis(result, data)
                return render_result(result, data)
            except Exception as exc:
                error = str(exc)

    if uploaded_data is not None:
        return page("""
        <div class="card">
            <h1>Review & Edit Uploaded Sample</h1>
            <p class="small">
                The uploaded values were loaded below. Edit them if required,
                then run the AI analysis.
            </p>

            <form method="POST">
                <input type="hidden" name="loaded" value="1">

                <label>Sample Name</label>
                <input name="sample_name"
                       value="{{ data.get('sample_name','Uploaded Sample') }}">

                <div class="grid">
                {% for f in features %}
                    <div>
                        <label>{{ labels[f] }}</label>
                        <input name="{{ f }}" type="number" step="any"
                               value="{{ data[f] }}" required>
                    </div>
                {% endfor %}
                </div>

                <div class="grid-2">
                    <div>
                        <label>Dross Type</label>
                        <select name="dross_type">
                            <option {% if data.get('dross_type')=='White Dross' %}selected{% endif %}>White Dross</option>
                            <option {% if data.get('dross_type')=='Black Dross' %}selected{% endif %}>Black Dross</option>
                            <option {% if data.get('dross_type')=='Salt Slag' %}selected{% endif %}>Salt Slag</option>
                        </select>
                    </div>

                    <div>
                        <label>XRD Phase</label>
                        <input name="xrd" value="{{ data.get('xrd','') }}">
                    </div>

                    <div>
                        <label>SEM Morphology</label>
                        <input name="sem" value="{{ data.get('sem','') }}">
                    </div>
                </div>

                <button type="submit">Analyze Edited Sample</button>
            </form>
        </div>
        """,
        data=uploaded_data,
        features=FEATURES,
        labels={f: f.replace("_", " ").title() for f in FEATURES})

    return page("""
    <div class="card">
        <h1>File + Manual Input</h1>

        {% if error %}
        <div class="error">{{ error }}</div>
        {% endif %}

        <p>
            First upload a CSV/Excel file. ReAlux will load the first sample
            and let you edit it before prediction.
        </p>

        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="file"
                   accept=".csv,.xlsx,.xls" required>
            <button type="submit">Load File</button>
        </form>
    </div>
    """, error=error)


# ============================================================
# MANUAL PREDICTION
# ============================================================

@app.route("/predict", methods=["POST"])
def predict():
    if require_login():
        return redirect(url_for("login"))

    try:
        data = {}
        for feature in FEATURES:
            data[feature] = float(request.form[feature])

        data["dross_type"] = request.form.get("dross_type", "Unknown")
        data["xrd"] = request.form.get("xrd", "Not provided")
        data["sem"] = request.form.get("sem", "Not provided")

        result = predict_data(
            data,
            request.form.get("sample_name", "Manual Sample")
        )

        save_analysis(result, data)
        return render_result(result, data)

    except Exception as exc:
        return page("""
        <div class="card">
            <div class="error">
                Invalid input: {{ error }}
            </div>
            <a class="btn" href="/manual">Back to Input</a>
        </div>
        """, error=str(exc))


# ============================================================
# RESULT DASHBOARD
# ============================================================

def render_result(result, data):
    return page("""
    <div class="card">
        <h1>ReAlux AI Analysis Result</h1>
        <p class="subtitle">
            Sample: <b>{{ result.sample_name }}</b>
        </p>

        <div class="notice">
            <b>Prototype AI:</b>
            Predictions shown here come from the included demonstration model.
            Validate the model against experimental data before industrial use.
        </div>
    </div>

    <div class="grid">
        <div class="box">
            <h3>Metal Recovery</h3>
            <div class="metric">{{ "%.2f"|format(result.metal_recovery) }}%</div>
        </div>

        <div class="box">
            <h3>Alumina Recovery</h3>
            <div class="metric">{{ "%.2f"|format(result.alumina_recovery) }}%</div>
        </div>

        <div class="box">
            <h3>Recovery Category</h3>
            <div class="metric {{ result.css_class }}">
                {{ result.category }}
            </div>
        </div>
    </div>

    <div class="grid">
        <div class="box">
            <h3>Confidence</h3>
            <div class="metric">{{ "%.1f"|format(result.confidence) }}%</div>
        </div>

        <div class="box">
            <h3>Environmental Score</h3>
            <div class="metric">{{ "%.1f"|format(result.environmental_score) }}/100</div>
        </div>

        <div class="box">
            <h3>Economic Score</h3>
            <div class="metric">{{ "%.1f"|format(result.economic_score) }}/100</div>
        </div>
    </div>

    <div class="card">
        <h2>AI Recommendation</h2>

        <h3>Recommended Recovery Route</h3>
        <div class="metric">{{ result.route }}</div>

        <h3>Why?</h3>
        <p>{{ result.reason }}</p>

        <h3>Potential Industrial Application</h3>
        <p><span class="badge">{{ result.application }}</span></p>
    </div>

    <div class="card">
        <h2>Recommended Process Parameters</h2>

        <div class="grid">
            <div class="box">
                <h3>Furnace</h3>
                <p>{{ result.furnace }}</p>
            </div>

            <div class="box">
                <h3>Temperature</h3>
                <p>{{ result.temperature }}</p>
            </div>

            <div class="box">
                <h3>Hydro pH</h3>
                <p>{{ result.hydro_ph }}</p>
            </div>

            <div class="box">
                <h3>Leaching Time</h3>
                <p>{{ result.leaching_time }}</p>
            </div>
        </div>

        <p class="small">
            * Process parameters are illustrative recommendation fields and
            require laboratory/pilot validation for a specific feedstock.
        </p>
    </div>

    <div class="card">
        <h2>Waste → Value</h2>

        <div class="grid">
            <div class="box"><b>1.</b><br>Aluminium Dross</div>
            <div class="box"><b>2.</b><br>AI Analysis</div>
            <div class="box"><b>3.</b><br>Recovery Prediction</div>
            <div class="box"><b>4.</b><br>Recommended Process</div>
            <div class="box"><b>5.</b><br>Industrial Product</div>
            <div class="box"><b>6.</b><br>Environmental Benefit</div>
        </div>
    </div>

    <a class="btn" href="/input-method">Analyze Another Sample</a>
    <a class="btn btn-secondary" href="/history">View History</a>
    <a class="btn btn-orange" href="/dashboard">Dashboard</a>
    """, result=result, data=data)


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():
    if require_login():
        return redirect(url_for("login"))

    conn = get_db()

    rows = conn.execute("""
        SELECT *
        FROM analyses
        WHERE email=?
        ORDER BY id DESC
        LIMIT 20
    """, (session["email"],)).fetchall()

    conn.close()

    if rows:
        df = pd.DataFrame([dict(r) for r in rows])
        avg_metal = df["metal_recovery"].mean()
        avg_alumina = df["alumina_recovery"].mean()
        high_count = int((df["category"] == "High Recovery").sum())
        total = len(df)
    else:
        avg_metal = avg_alumina = 0
        high_count = total = 0

    return page("""
    <div class="card">
        <h1>ReAlux Industrial Dashboard</h1>
        <p class="subtitle">
            Logged in as {{ email }}
        </p>
    </div>

    <div class="grid">
        <div class="box">
            <h3>Samples Analyzed</h3>
            <div class="metric">{{ total }}</div>
        </div>

        <div class="box">
            <h3>Average Metal Recovery</h3>
            <div class="metric">{{ "%.2f"|format(avg_metal) }}%</div>
        </div>

        <div class="box">
            <h3>Average Alumina Recovery</h3>
            <div class="metric">{{ "%.2f"|format(avg_alumina) }}%</div>
        </div>
    </div>

    <div class="card">
        <h2>Recovery Trend</h2>

        {% if rows %}
        <table>
            <tr>
                <th>Sample</th>
                <th>Metal Recovery</th>
                <th>Alumina Recovery</th>
                <th>Category</th>
                <th>Route</th>
            </tr>

            {% for r in rows %}
            <tr>
                <td>{{ r["sample_name"] }}</td>
                <td>{{ "%.2f"|format(r["metal_recovery"]) }}%</td>
                <td>{{ "%.2f"|format(r["alumina_recovery"]) }}%</td>
                <td>{{ r["category"] }}</td>
                <td>{{ r["route"] }}</td>
            </tr>
            {% endfor %}
        </table>
        {% else %}
        <p>No analyses yet.</p>
        {% endif %}
    </div>

    <div class="card">
        <h2>AI Insights</h2>
        <ul>
            <li>{{ high_count }} of the latest {{ total }} samples are classified as High Recovery.</li>
            <li>Use historical results to identify composition–recovery trends.</li>
            <li>Use validated experimental data to retrain and improve the model.</li>
        </ul>
    </div>

    <a class="btn" href="/input-method">New Analysis</a>
    <a class="btn btn-secondary" href="/history">Full History</a>
    <a class="btn btn-orange" href="/download-history">Download CSV</a>
    """,
    email=session["email"],
    rows=rows,
    avg_metal=avg_metal,
    avg_alumina=avg_alumina,
    high_count=high_count,
    total=total)


# ============================================================
# HISTORY
# ============================================================

@app.route("/history")
def history():
    if require_login():
        return redirect(url_for("login"))

    conn = get_db()
    records = conn.execute("""
        SELECT *
        FROM analyses
        WHERE email=?
        ORDER BY id DESC
    """, (session["email"],)).fetchall()
    conn.close()

    return page("""
    <div class="card">
        <h1>Analysis History</h1>

        {% if records %}
        <table>
            <tr>
                <th>Sample</th>
                <th>Metal %</th>
                <th>Metal Recovery</th>
                <th>Alumina Recovery</th>
                <th>Category</th>
                <th>Route</th>
                <th>Application</th>
                <th>Date</th>
            </tr>

            {% for r in records %}
            <tr>
                <td>{{ r["sample_name"] }}</td>
                <td>{{ "%.2f"|format(r["metal_pct"]) }}</td>
                <td>{{ "%.2f"|format(r["metal_recovery"]) }}%</td>
                <td>{{ "%.2f"|format(r["alumina_recovery"]) }}%</td>
                <td>{{ r["category"] }}</td>
                <td>{{ r["route"] }}</td>
                <td>{{ r["application"] }}</td>
                <td>{{ r["created_at"] }}</td>
            </tr>
            {% endfor %}
        </table>
        {% else %}
        <p>No analysis records available.</p>
        {% endif %}
    </div>

    <a class="btn" href="/input-method">New Analysis</a>
    <a class="btn btn-secondary" href="/dashboard">Dashboard</a>
    <a class="btn btn-orange" href="/download-history">Download CSV</a>
    """, records=records)


# ============================================================
# DOWNLOAD HISTORY
# ============================================================

@app.route("/download-history")
def download_history():
    if require_login():
        return redirect(url_for("login"))

    conn = get_db()
    rows = conn.execute("""
        SELECT *
        FROM analyses
        WHERE email=?
        ORDER BY id DESC
    """, (session["email"],)).fetchall()
    conn.close()

    df = pd.DataFrame([dict(r) for r in rows])

    if df.empty:
        df = pd.DataFrame(
            columns=[
                "sample_name",
                "metal_recovery",
                "alumina_recovery",
                "category",
                "route"
            ]
        )

    output = io.BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)

    return send_file(
        output,
        mimetype="text/csv",
        as_attachment=True,
        download_name="realux_analysis_history.csv"
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    init_db()

    print("\n==============================================")
    print(" ReAlux Flask Application")
    print(" http://127.0.0.1:5000")
    print("==============================================\n")

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000,
        use_reloader=False
    )
