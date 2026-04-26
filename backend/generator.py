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
        steam_summary = ""
        if steam_data and not steam_data.get("error"):
            steam_summary = f"""
STEAM LIBRARY:
- Display name: {steam_data.get("display_name")}
- Total games owned: {steam_data.get("total_games")}
- Games never played: {steam_data.get("never_played_count")} ({steam_data.get("never_played_percent")}% of library)
- Total hours across all games: {steam_data.get("total_hours")}
- Most played game: {steam_data.get("most_played", {}).get("name")} ({steam_data.get("most_played", {}).get("hours")} hours)
- Top 5 games by hours: {", ".join([f"{g['name']} ({g['hours']}h)" for g in steam_data.get("top_games", [])])}
- Recently played (last 2 weeks): {", ".join([f"{g['name']} ({g['hours_last_2_weeks']}h)" for g in steam_data.get("recently_played", [])])}
"""

        riot_summary = ""
        if riot_data and not riot_data.get("error"):
            games = riot_data.get("games", {})
            lol = games.get("league_of_legends", {})
            val = games.get("valorant", {})
            tft = games.get("tft", {})

            if lol:
                rank = lol.get("rank", {})
                stats = lol.get("recent_stats", {})
                riot_summary += f"""
LEAGUE OF LEGENDS:
- Rank: {rank.get("tier")} {rank.get("rank")} — {rank.get("lp")} LP
- Record: {rank.get("wins")}W / {rank.get("losses")}L ({rank.get("win_rate")}% win rate)
- Summoner level: {lol.get("summoner_level")}
- Recent KDA: {stats.get("kda")} ({stats.get("total_kills")}K / {stats.get("total_deaths")}D / {stats.get("total_assists")}A)
- Average vision score: {stats.get("avg_vision_score")}
- Top champions: {", ".join(lol.get("top_champions", []))}
"""

            if tft:
                tft_rank = tft.get("rank", {})
                riot_summary += f"""
TEAMFIGHT TACTICS:
- Rank: {tft_rank.get("tier")} {tft_rank.get("rank")} — {tft_rank.get("lp")} LP
- Record: {tft_rank.get("wins")}W / {tft_rank.get("losses")}L ({tft_rank.get("win_rate")}% win rate)
"""

            if val:
                val_stats = val.get("recent_stats", {})
                riot_summary += f"""
VALORANT:
- Recent KDA: {val_stats.get("kda")} ({val_stats.get("kills")}K / {val_stats.get("deaths")}D / {val_stats.get("assists")}A)
- Top agents: {", ".join(val.get("top_agents", []))}
"""

        prompt = f"""
Write an ironic Wikipedia article about a gamer named "{display_name}".
Use ALL of the real stats below — weave them naturally into the prose.
Be funny, specific, and encyclopedic. Reference actual numbers and game names.

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