import os
import sqlite3
import hashlib
import secrets
from datetime import datetime


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_DIR = os.path.join(BASE_DIR, "database")
DB_PATH = os.path.join(DB_DIR, "realux.db")

os.makedirs(DB_DIR, exist_ok=True)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def _conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def init_db():
    with _conn() as c:

        # -------------------------
        # USERS TABLE
        # -------------------------
        c.execute("""
            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)

        # -------------------------
        # ANALYSES TABLE
        # -------------------------
        c.execute("""
            CREATE TABLE IF NOT EXISTS analyses(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                sample_id TEXT,
                sample_type TEXT,
                source TEXT,
                test_method TEXT,
                input_method TEXT,
                composition_json TEXT,
                metal_recovery REAL,
                alumina_recovery REAL,
                recovery_category TEXT,
                best_method TEXT,
                method_reason TEXT,
                risk_level TEXT,
                model_used TEXT,
                model_type TEXT,
                r2_metal REAL,
                mae_metal REAL,
                rmse_metal REAL,
                r2_alumina REAL,
                mae_alumina REAL,
                rmse_alumina REAL,
                created_at TEXT NOT NULL
            )
        """)

        # -------------------------
        # REPORTS TABLE
        # -------------------------
        c.execute("""
            CREATE TABLE IF NOT EXISTS reports(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                filepath TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)


# ============================================================
# PASSWORD HASHING
# ============================================================

def _hash(password, salt):
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt.encode(),
        200000
    ).hex()


# ============================================================
# USER FUNCTIONS
# ============================================================

def create_user(name, email, password):
    salt = secrets.token_hex(16)

    password_hash = _hash(
        password,
        salt
    )

    try:
        with _conn() as c:

            c.execute(
                """
                INSERT INTO users(
                    name,
                    email,
                    password_hash,
                    salt,
                    created_at
                )
                VALUES(?,?,?,?,?)
                """,
                (
                    name,
                    email.lower().strip(),
                    password_hash,
                    salt,
                    datetime.now().isoformat()
                )
            )

        return True, "Account created"

    except sqlite3.IntegrityError:
        return False, "Email already registered"


def authenticate_user(email, password):

    with _conn() as c:

        row = c.execute(
            """
            SELECT *
            FROM users
            WHERE email=?
            """,
            (
                email.lower().strip(),
            )
        ).fetchone()

    if not row:
        return None

    if _hash(password, row["salt"]) != row["password_hash"]:
        return None

    return dict(row)


def get_user_by_id(user_id):

    with _conn() as c:

        row = c.execute(
            """
            SELECT
                id,
                name,
                email,
                created_at
            FROM users
            WHERE id=?
            """,
            (
                int(user_id),
            )
        ).fetchone()

    return dict(row) if row else None


# ============================================================
# ANALYSIS FUNCTIONS
# ============================================================

def save_analysis(user_id, data):

    keys = [
        "sample_id",
        "sample_type",
        "source",
        "test_method",
        "input_method",
        "composition_json",
        "metal_recovery",
        "alumina_recovery",
        "recovery_category",
        "best_method",
        "method_reason",
        "risk_level",
        "model_used",
        "model_type",
        "r2_metal",
        "mae_metal",
        "rmse_metal",
        "r2_alumina",
        "mae_alumina",
        "rmse_alumina"
    ]

    values = [
        data.get(key)
        for key in keys
    ]

    columns = ",".join(keys)

    placeholders = ",".join(
        ["?"] * len(keys)
    )

    with _conn() as c:

        cursor = c.execute(
            f"""
            INSERT INTO analyses(
                user_id,
                {columns},
                created_at
            )
            VALUES(
                ?,
                {placeholders},
                ?
            )
            """,
            [
                user_id,
                *values,
                datetime.now().isoformat()
            ]
        )

        return cursor.lastrowid


def get_user_analyses(user_id):

    with _conn() as c:

        rows = c.execute(
            """
            SELECT *
            FROM analyses
            WHERE user_id=?
            ORDER BY id DESC
            """,
            (
                user_id,
            )
        ).fetchall()

    return [
        dict(row)
        for row in rows
    ]


def get_analysis_by_id(analysis_id):

    with _conn() as c:

        row = c.execute(
            """
            SELECT *
            FROM analyses
            WHERE id=?
            """,
            (
                analysis_id,
            )
        ).fetchone()

    return dict(row) if row else None


# ============================================================
# REPORT FUNCTIONS
# ============================================================

def save_report_record(
    analysis_id,
    user_id,
    filepath
):

    with _conn() as c:

        cursor = c.execute(
            """
            INSERT INTO reports(
                analysis_id,
                user_id,
                filepath,
                created_at
            )
            VALUES(?,?,?,?)
            """,
            (
                analysis_id,
                user_id,
                filepath,
                datetime.now().isoformat()
            )
        )

        return cursor.lastrowid


def get_user_reports(user_id):

    with _conn() as c:

        rows = c.execute(
            """
            SELECT
                r.*,
                a.sample_id,
                a.test_method
            FROM reports r

            JOIN analyses a
                ON a.id = r.analysis_id

            WHERE r.user_id=?

            ORDER BY r.id DESC
            """,
            (
                user_id,
            )
        ).fetchall()

    return [
        dict(row)
        for row in rows
    ]


def get_report_by_id(report_id):

    with _conn() as c:

        row = c.execute(
            """
            SELECT *
            FROM reports
            WHERE id=?
            """,
            (
                report_id,
            )
        ).fetchone()

    return dict(row) if row else None


# ============================================================
# DELETE REPORT
# ============================================================

def delete_report(
    report_id,
    user_id
):
    """
    Delete a report only if it belongs
    to the currently logged-in user.

    Also removes the generated PDF
    from the reports folder.
    """

    # --------------------------------
    # Find report belonging to user
    # --------------------------------

    with _conn() as c:

        report = c.execute(
            """
            SELECT *
            FROM reports
            WHERE id=?
            AND user_id=?
            """,
            (
                report_id,
                user_id
            )
        ).fetchone()

        if not report:
            return False

        filepath = report["filepath"]

        # -----------------------------
        # Delete database record
        # -----------------------------

        c.execute(
            """
            DELETE FROM reports
            WHERE id=?
            AND user_id=?
            """,
            (
                report_id,
                user_id
            )
        )

    # --------------------------------
    # Delete PDF file from disk
    # --------------------------------

    if filepath and os.path.exists(filepath):

        try:
            os.remove(filepath)

        except OSError:
            # Database record is already deleted.
            # Ignore filesystem deletion errors.
            pass

    return True