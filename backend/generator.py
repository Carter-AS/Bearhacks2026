import requests
import json

GEMMA_API_KEY = "AIzaSyDKmnjGahYt-mvjZgc-7LTs9qnSx6-avro"

def generate_wiki_page(riot_data: dict, steam_data: dict) -> dict:
    try:
        # Build a prompt with the real stats injected
        prompt = build_prompt(riot_data, steam_data)

        response = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemma-3-27b-it:generateContent",
            headers={"Content-Type": "application/json"},
            params={"key": GEMMA_API_KEY},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.9,
                    "maxOutputTokens": 2048,
                }
            }
        )

        result = response.json()
        raw_text = result["candidates"][0]["content"]["parts"][0]["text"]

        # Strip markdown fences if present
        clean = raw_text.strip()
        if clean.startswith("```json"):
            clean = clean[7:]
        if clean.startswith("```"):
            clean = clean[3:]
        if clean.endswith("```"):
            clean = clean[:-3]

        sections = json.loads(clean.strip())
        return {"success": True, "sections": sections}

    except Exception as e:
        return {"success": False, "error": str(e)}


def build_prompt(riot_data: dict, steam_data: dict) -> str:
    username = riot_data.get("username", "Unknown")
    level = riot_data.get("summoner_level", 0)
    rank = riot_data.get("rank", {})
    stats = riot_data.get("recent_stats", {})
    champs = riot_data.get("top_champions", [])

    tier = rank.get("tier", "UNRANKED")
    division = rank.get("rank", "")
    lp = rank.get("lp", 0)
    wins = rank.get("wins", 0)
    losses = rank.get("losses", 0)
    win_rate = rank.get("win_rate", 0)
    deaths = stats.get("total_deaths", 0)
    kills = stats.get("total_kills", 0)
    assists = stats.get("total_assists", 0)
    kda = stats.get("kda", 0)
    vision = stats.get("avg_vision_score", 0)

    steam_section = ""
    if steam_data and not steam_data.get("error"):
        total_hours = steam_data.get("total_hours", 0)
        total_games = steam_data.get("total_games", 0)
        never_played = steam_data.get("never_played", 0)
        most_played = steam_data.get("most_played", {})
        steam_section = f"""
Steam Profile:
- Total games owned: {total_games}
- Games never launched: {never_played}
- Total hours across all games: {total_hours}
- Most played: {most_played.get('name', 'N/A')} ({most_played.get('hours', 0)} hours)
"""

    return f"""
You are writing an ironic, Wikipedia-style encyclopedia article about a gamer. 
Use dry, encyclopedic prose with subtle humor. Never break character — write as if 
this is a real Wikipedia article. Be specific and reference the actual stats provided. 
Be witty but not mean-spirited.

Here are the player's real stats:

League of Legends:
- Username: {username}
- Summoner level: {level}
- Rank: {tier} {division} ({lp} LP)
- Record: {wins}W {losses}L ({win_rate}% win rate)
- Recent stats (last 10 games): {kills} kills, {deaths} deaths, {assists} assists (KDA: {kda})
- Average vision score: {vision}
- Most played champions: {', '.join(champs) if champs else 'Unknown'}
{steam_section}

Return ONLY a JSON array of sections, no preamble, no markdown fences. Format:
[
  {{"title": "Early life and account creation", "content": "..."}},
  {{"title": "Career", "content": "..."}},
  {{"title": "Controversies", "content": "..."}},
  {{"title": "Legacy and statistics", "content": "..."}},
  {{"title": "Trivia", "content": "..."}}
]

Each content field should be 2-4 sentences of dry, ironic Wikipedia prose based on the real stats.
Make the humor come from the encyclopedic framing, not from insults.
Reference specific stats naturally within the prose.
"""