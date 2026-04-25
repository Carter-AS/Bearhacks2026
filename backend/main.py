from flask import Flask, jsonify, request
from flask_cors import CORS
from data_fetcher import fetch_riot_data, fetch_steam_data
from generator import generate_wiki_page

app = Flask(__name__)
CORS(app)


# ── Health check ─────────────────────────────────────────────
@app.route("/api/hello")
def hello():
    return jsonify({"message": "Hello, World!"})


# ── Generate a WikiGamer page ─────────────────────────────────
# Accepts: { "riot_username": "...", "steam_username": "..." }
# Queues a generation job and returns a job_id to poll
@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.get_json()
    riot_username = data.get("riot_username")
    steam_username = data.get("steam_username")

    if not riot_username and not steam_username:
        return jsonify({"error": "At least one username is required"}), 400

    riot_data = fetch_riot_data(riot_username) if riot_username else {}
    steam_data = fetch_steam_data(steam_username) if steam_username else {}

    if riot_data.get("error") or steam_data.get("error"):
        return jsonify({"error": "Failed to fetch player data", "details": {
            "riot": riot_data.get("error"),
            "steam": steam_data.get("error"),
        }}), 400

    result = generate_wiki_page(riot_data, steam_data)

    if not result["success"]:
        return jsonify({"error": "Generation failed", "details": result["error"]}), 500

    return jsonify({
        "username": riot_username or steam_username,
        "sections": result["sections"],
        "raw_data": {
            "riot": riot_data,
            "steam": steam_data,
        }
    }), 200


# ── Poll job status ───────────────────────────────────────────
# Frontend polls this until status is "done"
@app.route("/api/job/<job_id>", methods=["GET"])
def job_status(job_id):
    # TODO: check Celery task status and return progress
    return jsonify({
        "job_id": job_id,
        "status": "pending",  # pending | processing | done | failed
        "progress": "Fetching stats...",
    })


# ── Fetch a saved WikiGamer page ──────────────────────────────
# Returns the full generated page by username
@app.route("/api/page/<username>", methods=["GET"])
def get_page(username):
    # TODO: query PostgreSQL for saved page
    return jsonify({
        "username": username,
        "page": None,
        "message": "Page not found (DB not connected yet)",
    }), 404


# ── Search saved pages ────────────────────────────────────────
# Query param: ?q=username
@app.route("/api/search", methods=["GET"])
def search():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "Search query is required"}), 400

    # TODO: full-text search against PostgreSQL
    return jsonify({
        "query": query,
        "results": [],
        "message": "Search not connected yet",
    })


# ── Claim a page (Auth0 protected) ───────────────────────────
# Accepts: { "username": "...", "auth0_token": "...", "quote": "...", "early_life": "..." }
@app.route("/api/claim", methods=["POST"])
def claim_page():
    data = request.get_json()
    username = data.get("username")
    auth0_token = data.get("auth0_token")

    if not username or not auth0_token:
        return jsonify({"error": "Username and auth token are required"}), 400

    # TODO: verify Auth0 token, link user to page in PostgreSQL
    return jsonify({
        "message": "Claim endpoint hit (Auth0 not connected yet)",
        "username": username,
    })


# ── Update claimed page (owner only) ─────────────────────────
# Owners can edit quote + early_life blurb, not the AI content
@app.route("/api/page/<username>/edit", methods=["PATCH"])
def edit_page(username):
    data = request.get_json()
    auth0_token = data.get("auth0_token")
    quote = data.get("quote")
    early_life = data.get("early_life")

    if not auth0_token:
        return jsonify({"error": "Auth token required"}), 401

    # TODO: verify ownership via Auth0, update editable fields in PostgreSQL
    return jsonify({
        "message": "Edit endpoint hit (Auth0 not connected yet)",
        "username": username,
        "updated_fields": {"quote": quote, "early_life": early_life},
    })


# ── Browse all pages (paginated) ──────────────────────────────
# Query params: ?page=1&sort=recent|views|controversial
@app.route("/api/pages", methods=["GET"])
def browse_pages():
    page = request.args.get("page", 1, type=int)
    sort = request.args.get("sort", "recent")

    # TODO: paginated query from PostgreSQL
    return jsonify({
        "page": page,
        "sort": sort,
        "results": [],
        "total": 0,
        "message": "Browse not connected yet",
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)