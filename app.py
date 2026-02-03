from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)
DB_NAME = "quantum_companies.db"


def get_sources():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT TRIM(source) FROM companies WHERE source IS NOT NULL")
    sources = [row[0] for row in cursor.fetchall()]
    conn.close()
    return sources


def get_data(search="", source=""):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    query = """
        SELECT c.company_name, p.product_name, c.source
        FROM companies c
        JOIN company_products cp ON c.company_id = cp.company_id
        JOIN products p ON cp.product_id = p.product_id
        WHERE 1=1
    """
    params = []

    if search:
        query += " AND (c.company_name LIKE ? OR p.product_name LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    if source:
        query += " AND LOWER(TRIM(c.source)) = LOWER(TRIM(?))"
        params.append(source)

    query += " ORDER BY c.company_name"

    cursor.execute(query, params)
    data = cursor.fetchall()
    conn.close()
    return data


@app.route("/", methods=["GET"])
def index():
    search = request.args.get("search", "")
    source = request.args.get("source", "")

    data = get_data(search, source)
    sources = get_sources()

    return render_template(
        "index.html",
        data=data,
        sources=sources,
        selected_source=source,
        search=search
    )


if __name__ == "__main__":
    app.run(debug=True)
