from flask import Flask, jsonify, request
from flask_cors import CORS
from data_fetcher import fetch_riot_data, fetch_steam_data
from generator import generate_wiki_page
from database import save_page, get_page, search_pages, browse_pages
from elevenlabs.client import ElevenLabs
import os
import random

app = Flask(__name__)
CORS(app)


# eleven labs
el_client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

@app.route("/api/narrate", methods=["POST"])
def narrate():
    data = request.get_json()
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        audio = el_client.text_to_speech.convert(
            voice_id="JBFqnCBsd6RMkjVDRZzb",  # "George" — sounds like a documentary narrator
            text=text,
            model_id="eleven_turbo_v2",
        )

        # Collect audio bytes
        audio_bytes = b"".join(audio)

        # Return as base64 so frontend can play it directly
        import base64
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

        return jsonify({"audio": audio_b64}), 200

    except Exception as e:
        print("ElevenLabs error:", e)
        return jsonify({"error": str(e)}), 500


@app.route("/api/random", methods=["GET"])
def random_page():
    data = browse_pages(page=1, sort="recent")
    results = data.get("results", [])
    if not results:
        return jsonify({"error": "No pages yet"}), 404
    pick = random.choice(results)
    return jsonify({"username": pick["username"]}), 200


@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.get_json()
    display_name = data.get("display_name", "").strip()
    riot_username = data.get("riot_username")
    steam_username = data.get("steam_username")

    if not display_name:
        return jsonify({"error": "Display name is required"}), 400
    if not riot_username and not steam_username:
        return jsonify({"error": "At least one game username is required"}), 400

    riot_data = fetch_riot_data(riot_username) if riot_username else {}
    print("riot_data result:", riot_data)

    steam_data = fetch_steam_data(steam_username) if steam_username else {}

    if riot_username and riot_data.get("error") and not riot_data.get("games"):
        return jsonify({"error": f"Riot ID not found. Make sure to use the format Name#TAG (e.g. Carter#NA1)"}), 404

    if steam_username and steam_data.get("error") and not steam_data.get("total_games"):
        return jsonify({"error": f"Steam error: {steam_data['error']}"}), 404
    
    result = generate_wiki_page(riot_data, steam_data, display_name)
    sections = result.get("sections", [])

    save_page(display_name.lower(), riot_data, steam_data, sections)

    return jsonify({
        "username": display_name.lower(),
        "sections": sections,
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

@app.route("/api/check/<display_name>", methods=["GET"])
def check_name(display_name):
    page = get_page(display_name.lower())
    if page:
        return jsonify({"taken": True}), 200
    return jsonify({"taken": False}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)


@app.route("/api/page/<username>/rename", methods=["PATCH"])
def rename_page(username):
    data = request.get_json()
    new_username = data.get("new_username", "").strip().lower()

    if not new_username:
        return jsonify({"error": "New username is required"}), 400

    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE pages SET username = %s, display_name = %s
            WHERE username = %s
        """, (new_username, new_username, username))
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"error": "Page not found"}), 404
        return jsonify({"message": "Renamed successfully", "username": new_username}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()