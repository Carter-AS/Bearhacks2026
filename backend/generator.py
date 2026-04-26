import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
import json

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

SYSTEM_INSTRUCTION = """You are an ironic Wikipedia editor writing humorous but affectionate articles about gamers.
Your tone is dry, formal, and encyclopedic — like a real Wikipedia article — but the content is gently absurd and self-aware.
Use phrases like "scholars disagree", "sources close to the player confirm", "investigators are baffled".
Never break character. Always sound like a real encyclopedia entry.
Reference specific stats from ALL games provided — League of Legends, Valorant, TFT, and Steam library data.
For Steam, highlight funny details like unplayed games, total hours, and most played games.
Return ONLY a valid JSON object with no markdown, no backticks, no preamble. Format:
{
  "sections": [
    {"title": "Early life and account creation", "content": "..."},
    {"title": "Career", "content": "..."},
    {"title": "Controversies", "content": "..."},
    {"title": "Legacy and statistics", "content": "..."},
    {"title": "Trivia", "content": "..."}
  ]
}"""

def generate_wiki_page(riot_data: dict, steam_data: dict, display_name: str = "") -> dict:
    try:
        available_sources = []
        
        riot_summary = ""
        if riot_data and not riot_data.get("error"):
            games = riot_data.get("games", {})
            lol = games.get("league_of_legends", {})
            tft = games.get("tft", {})

            if lol:
                available_sources.append("League of Legends")
                rank = lol.get("rank", {})
                stats = lol.get("recent_stats", {})
                top_champs = lol.get("top_champions", [])
                riot_summary += f"""```
LEAGUE OF LEGENDS:
- Rank: {rank.get("tier")} {rank.get("rank")} — {rank.get("lp")} LP
- Record: {rank.get("wins")}W / {rank.get("losses")}L ({rank.get("win_rate")}% win rate)
- Summoner level: {lol.get("summoner_level")}
- Recent KDA: {stats.get("kda")} ({stats.get("total_kills")}K / {stats.get("total_deaths")}D / {stats.get("total_assists")}A)
- Average vision score: {stats.get("avg_vision_score")}
- Top champions: {", ".join(top_champs)}
- Most played champion: {top_champs[0] if top_champs else "Unknown"} (mention this naturally in the Career section)
"""
            if tft:
                available_sources.append("TFT")
                tft_rank = tft.get("rank", {})
                riot_summary += f"""
TEAMFIGHT TACTICS:
- Rank: {tft_rank.get("tier")} {tft_rank.get("rank")} — {tft_rank.get("lp")} LP
- Record: {tft_rank.get("wins")}W / {tft_rank.get("losses")}L ({tft_rank.get("win_rate")}% win rate)
"""

        steam_summary = ""
        if steam_data and not steam_data.get("error"):
            available_sources.append("Steam")
            most_played = steam_data.get("most_played", {})
            steam_summary += f"""
STEAM LIBRARY:
- Total games owned: {steam_data.get("total_games")}
- Games never played: {steam_data.get("never_played_count")} ({steam_data.get("never_played_percent")}% of library)
- Total hours: {steam_data.get("total_hours")}
- Most played game: {most_played.get("name")} ({most_played.get("hours")} hours) (mention this prominently in the Legacy section)
- Top 5 games: {", ".join([f"{g['name']} ({g['hours']}h)" for g in steam_data.get("top_games", [])])}
- Recently played: {", ".join([f"{g['name']} ({g['hours_last_2_weeks']}h)" for g in steam_data.get("recently_played", [])])}
"""

        # Tell Gemma exactly what data exists and what doesn't
        not_available = []
        all_possible = ["League of Legends", "Valorant", "TFT", "Steam"]
        for source in all_possible:
            if source not in available_sources:
                not_available.append(source)

        prompt = f"""
Write an ironic Wikipedia article about a gamer named "{display_name}".

AVAILABLE DATA SOURCES: {", ".join(available_sources) if available_sources else "None"}
DO NOT MENTION OR INVENT DATA FOR: {", ".join(not_available) if not_available else "None"}

CRITICAL: Only reference games and platforms listed in AVAILABLE DATA SOURCES above.
Do NOT mention {", ".join(not_available)} at all — not even as a joke or speculation.
Every stat you reference must come directly from the data below. Do not invent any numbers.

{riot_summary}
{steam_summary}

Generate all 5 sections now.
"""

        response = client.models.generate_content(
            model="gemma-4-26b-a4b-it",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
            ),
            contents=prompt,
        )

        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()

        parsed = json.loads(text)
        return {"sections": parsed.get("sections", []), "username": display_name}

    except Exception as e:
        print("Generation error:", e)
        return {"sections": [], "username": display_name}