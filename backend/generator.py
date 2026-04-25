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

def generate_wiki_page(riot_data: dict, steam_data: dict) -> dict:
    try:
        prompt = f"""
Write an ironic Wikipedia article about this gamer using their real stats below.
Be funny but grounded in the actual numbers — reference specific stats like deaths, win rate, vision score, and champion choices.

RIOT DATA:
{json.dumps(riot_data, indent=2)}

STEAM DATA:
{json.dumps(steam_data, indent=2)}

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
        # Strip markdown fences if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()

        parsed = json.loads(text)
        return {"sections": parsed.get("sections", []), "username": riot_data.get("username", "")}

    except Exception as e:
        print("Generation error:", e)
        return {"sections": [], "username": riot_data.get("username", "")}