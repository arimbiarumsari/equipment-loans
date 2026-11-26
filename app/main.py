import os
import time

import psycopg2
import psycopg2.extras
from flask import Flask, jsonify, request

app = Flask(__name__)

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://equipment:equipment@db:5432/equipment"
)
VALID_STATUS = {"available", "borrowed"}


def get_conn():
    return psycopg2.connect(DATABASE_URL)


def init_db(retries=10, delay=3):
    """Create table on startup; retry while the db container is booting."""
    for attempt in range(1, retries + 1):
        try:
            with get_conn() as conn, conn.cursor() as cur:
                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS equipment (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        category VARCHAR(50) NOT NULL,
                        status VARCHAR(20) NOT NULL DEFAULT 'available',
                        borrower VARCHAR(100),
                        created_at TIMESTAMP NOT NULL DEFAULT NOW()
                    )
                    """
                )
            return
        except psycopg2.OperationalError:
            print(f"DB not ready (attempt {attempt}/{retries})", flush=True)
            time.sleep(delay)
    raise RuntimeError("Database unavailable")


def query(sql, params=(), one=False):
    with get_conn() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            if cur.description is None:
                return cur.rowcount
            rows = cur.fetchall()
            return (rows[0] if rows else None) if one else rows


@app.get("/health")
def health():
    try:
        query("SELECT 1")
        return jsonify(status="ok", database="connected")
    except Exception as exc:
        return jsonify(status="error", detail=str(exc)), 503


@app.post("/equipment")
def create_equipment():
    data = request.get_json(silent=True) or {}
    if not data.get("name") or not data.get("category"):
        return jsonify(error="'name' and 'category' are required"), 400
    row = query(
        "INSERT INTO equipment (name, category) VALUES (%s, %s) RETURNING *",
        (data["name"], data["category"]),
        one=True,
    )
    return jsonify(row), 201


@app.get("/equipment")
def list_equipment():
    return jsonify(query("SELECT * FROM equipment ORDER BY id"))


@app.get("/equipment/<int:item_id>")
def get_equipment(item_id):
    row = query("SELECT * FROM equipment WHERE id = %s", (item_id,), one=True)
    if not row:
        return jsonify(error="not found"), 404
    return jsonify(row)


@app.put("/equipment/<int:item_id>")
def update_equipment(item_id):
    data = request.get_json(silent=True) or {}
    current = query("SELECT * FROM equipment WHERE id = %s", (item_id,), one=True)
    if not current:
        return jsonify(error="not found"), 404

    name = data.get("name", current["name"])
    category = data.get("category", current["category"])
    status = data.get("status", current["status"])
    borrower = data.get("borrower", current["borrower"])

    if status not in VALID_STATUS:
        return jsonify(error=f"status must be one of {sorted(VALID_STATUS)}"), 400
    if status == "available":
        borrower = None
    elif not borrower:
        return jsonify(error="'borrower' is required when status is 'borrowed'"), 400

    row = query(
        """UPDATE equipment
           SET name=%s, category=%s, status=%s, borrower=%s
           WHERE id=%s RETURNING *""",
        (name, category, status, borrower, item_id),
        one=True,
    )
    return jsonify(row)


@app.delete("/equipment/<int:item_id>")
def delete_equipment(item_id):
    deleted = query("DELETE FROM equipment WHERE id = %s", (item_id,))
    if not deleted:
        return jsonify(error="not found"), 404
    return "", 204


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
