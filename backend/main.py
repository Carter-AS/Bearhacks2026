from flask import Flask, jsonify, request
from flask_cors import CORS
from data_fetcher import fetch_riot_data, fetch_steam_data
from generator import generate_wiki_page
from database import save_page, get_page, search_pages, browse_pages

app = Flask(__name__)
CORS(app)


@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.get_json()
    riot_username = data.get("riot_username")
    steam_username = data.get("steam_username")

    if not riot_username and not steam_username:
        return jsonify({"error": "At least one username is required"}), 400

    riot_data = fetch_riot_data(riot_username) if riot_username else {}
    steam_data = fetch_steam_data(steam_username) if steam_username else {}

    result = generate_wiki_page(riot_data, steam_data)
    sections = result.get("sections", [])
    username = riot_username or steam_username

    save_page(username, riot_data, steam_data, sections)

    return jsonify({
        "username": username,
        "sections": sections,
        "raw_data": {"riot": riot_data, "steam": steam_data},
    }), 200


@app.route("/api/page/<username>", methods=["GET"])
def get_page_route(username):
    page = get_page(username)
    if not page:
        return jsonify({"error": "Page not found"}), 404
    return jsonify({"username": username, "page": page}), 200


@app.route("/api/search", methods=["GET"])
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "Query required"}), 400
    results = search_pages(query)
    return jsonify({"query": query, "results": results}), 200


@app.route("/api/pages", methods=["GET"])
def browse():
    page = request.args.get("page", 1, type=int)
    sort = request.args.get("sort", "recent")
    data = browse_pages(page, sort)
    return jsonify(data), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)