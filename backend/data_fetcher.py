import requests
import os
from dotenv import load_dotenv

load_dotenv()

RIOT_API_KEY = os.getenv("RIOT_API_KEY")
STEAM_API_KEY = os.getenv("STEAM_API_KEY")
RIOT_REGION = os.getenv("RIOT_REGION", "na1")

# ── Riot Data ─────────────────────────────────────────────────

def fetch_riot_data(username: str) -> dict:
    try:
        if "#" in username:
            game_name, tag_line = username.split("#", 1)
        else:
            game_name, tag_line = username, "NA1"

        # 1. Get PUUID
        account_url = (
            f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id"
            f"/{game_name}/{tag_line}?api_key={RIOT_API_KEY}"
        )
        account_response = requests.get(account_url)
        account = account_response.json()
        puuid = account.get("puuid")

        if not puuid:
            return {"error": "Riot user not found"}


        result = {"username": username,
                  "champ_image_url": None,
                    "games": {}
                   }

        # 2. League of Legends
        try:
            summoner_url = (
                f"https://{RIOT_REGION}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid"
                f"/{puuid}?api_key={RIOT_API_KEY}"
            )
            summoner = requests.get(summoner_url).json()
            summoner_level = summoner.get("summonerLevel", 0)

            ranked_url = (
                f"https://{RIOT_REGION}.api.riotgames.com/lol/league/v4/entries/by-puuid"
                f"/{puuid}?api_key={RIOT_API_KEY}"
            )
            ranked_data = requests.get(ranked_url).json()

            lol_rank = {}
            tft_rank = {}
            for entry in ranked_data:
                wins = entry.get("wins", 0)
                losses = entry.get("losses", 0)
                total = wins + losses
                info = {
                    "tier": entry.get("tier", "UNRANKED"),
                    "rank": entry.get("rank", ""),
                    "lp": entry.get("leaguePoints", 0),
                    "wins": wins,
                    "losses": losses,
                    "total_games": total,
                    "win_rate": round((wins / total) * 100) if total > 0 else 0,
                }
                if entry.get("queueType") == "RANKED_SOLO_5x5":
                    lol_rank = info
                elif entry.get("queueType") == "RANKED_TFT":
                    tft_rank = info

            # LoL match history
            matches_url = (
                f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid"
                f"/{puuid}/ids?start=0&count=10&api_key={RIOT_API_KEY}"
            )
            match_ids = requests.get(matches_url).json()

            total_deaths = total_kills = total_assists = 0
            champion_counts = {}
            vision_scores = []

            for match_id in match_ids[:10]:
                match_url = (
                    f"https://americas.api.riotgames.com/lol/match/v5/matches"
                    f"/{match_id}?api_key={RIOT_API_KEY}"
                )
                match = requests.get(match_url).json()
                for p in match.get("info", {}).get("participants", []):
                    if p.get("puuid") == puuid:
                        total_deaths += p.get("deaths", 0)
                        total_kills += p.get("kills", 0)
                        total_assists += p.get("assists", 0)
                        vision_scores.append(p.get("visionScore", 0))
                        champ = p.get("championName", "Unknown")
                        champion_counts[champ] = champion_counts.get(champ, 0) + 1

            avg_vision = round(sum(vision_scores) / len(vision_scores)) if vision_scores else 0
            top_champions = sorted(champion_counts, key=champion_counts.get, reverse=True)[:3]
            
            top_champ = top_champions[0] if top_champions else None
            if top_champ:
                result["champ_image_url"] = f"https://ddragon.leagueoflegends.com/cdn/img/champion/loading/{top_champ}_0.jpg"


            result["games"]["league_of_legends"] = {
                "summoner_level": summoner_level,
                "rank": lol_rank,
                "recent_stats": {
                    "total_deaths": total_deaths,
                    "total_kills": total_kills,
                    "total_assists": total_assists,
                    "avg_vision_score": avg_vision,
                    "kda": round((total_kills + total_assists) / max(total_deaths, 1), 2),
                },
                "top_champions": top_champions,
            }

            if tft_rank:
                result["games"]["tft"] = {"rank": tft_rank}

        except Exception as e:
            print("LoL/TFT fetch error:", e)

        # 3. Valorant
        try:
            val_ranked_url = (
                f"https://americas.api.riotgames.com/val/ranked/v1/by-puuid/{puuid}"
                f"?api_key={RIOT_API_KEY}"
            )
            val_ranked = requests.get(val_ranked_url)

            val_matches_url = (
                f"https://americas.api.riotgames.com/val/match/v1/matchlists/by-puuid/{puuid}"
                f"?api_key={RIOT_API_KEY}"
            )
            val_matches_response = requests.get(val_matches_url)

            if val_matches_response.status_code == 200:
                val_matches = val_matches_response.json()
                history = val_matches.get("history", [])[:10]

                val_kills = val_deaths = val_assists = 0
                agent_counts = {}

                for match_entry in history:
                    match_id = match_entry.get("matchId")
                    match_url = (
                        f"https://americas.api.riotgames.com/val/match/v1/matches/{match_id}"
                        f"?api_key={RIOT_API_KEY}"
                    )
                    match = requests.get(match_url).json()
                    players = match.get("players", {}).get("allPlayers", [])
                    for p in players:
                        if p.get("puuid") == puuid:
                            stats = p.get("stats", {})
                            val_kills += stats.get("kills", 0)
                            val_deaths += stats.get("deaths", 0)
                            val_assists += stats.get("assists", 0)
                            agent = p.get("characterId", "Unknown")
                            agent_counts[agent] = agent_counts.get(agent, 0) + 1

                top_agents = sorted(agent_counts, key=agent_counts.get, reverse=True)[:3]

                result["games"]["valorant"] = {
                    "recent_stats": {
                        "kills": val_kills,
                        "deaths": val_deaths,
                        "assists": val_assists,
                        "kda": round((val_kills + val_assists) / max(val_deaths, 1), 2),
                    },
                    "top_agents": top_agents,
                }
            else:
                print("Valorant not available or player hasn't played:", val_matches_response.status_code)

            print("Valorant match response status:", val_matches_response.status_code)
            print("Valorant match response:", val_matches_response.text[:500])


        except Exception as e:
            print("Valorant fetch error:", e)

        return result

    except Exception as e:
        return {"error": str(e)}


# ── Steam Data ────────────────────────────────────────────────

def fetch_steam_data(steam_id: str) -> dict:
    try:
        if not steam_id or not steam_id.isdigit() or len(steam_id) != 17:
            return {"error": "Invalid Steam ID — must be a 17-digit number"}

        # 1. Get profile info
        profile_url = (
            f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"
            f"?key={STEAM_API_KEY}&steamids={steam_id}"
        )
        profile_data = requests.get(profile_url).json()
        players = profile_data.get("response", {}).get("players", [])

        if not players:
            return {"error": "Steam profile not found or is private"}

        player = players[0]

        # 2. Get owned games
        games_url = (
            f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
            f"?key={STEAM_API_KEY}&steamid={steam_id}"
            f"&include_appinfo=1&include_played_free_games=1&format=json"
        )
        games_data = requests.get(games_url).json()
        games = games_data.get("response", {}).get("games", [])

        if not games:
            return {"error": "No games found — Steam profile games may be private"}

        never_played = [g for g in games if g.get("playtime_forever", 0) == 0]
        played_games = [g for g in games if g.get("playtime_forever", 0) > 0]
        played_sorted = sorted(played_games, key=lambda g: g.get("playtime_forever", 0), reverse=True)

        top_games = [
            {
                "name": g.get("name", "Unknown"),
                "hours": round(g.get("playtime_forever", 0) / 60),
            }
            for g in played_sorted[:5]
        ]

        total_hours = round(sum(g.get("playtime_forever", 0) for g in games) / 60)

        # 3. Get recently played
        recent_url = (
            f"https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/"
            f"?key={STEAM_API_KEY}&steamid={steam_id}&count=5&format=json"
        )
        recent_data = requests.get(recent_url).json()
        recently_played = [
            {
                "name": g.get("name", "Unknown"),
                "hours_last_2_weeks": round(g.get("playtime_2weeks", 0) / 60, 1),
            }
            for g in recent_data.get("response", {}).get("games", [])
        ]
        most_played_game = played_sorted[0] if played_sorted else None
        cover_url = None
        if most_played_game:
            appid = most_played_game.get("appid")
            cover_url = f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/header.jpg"

        return {
            "display_name": player.get("personaname", steam_id),
            "steam_id": steam_id,
            "cover_url": cover_url,                    
            "most_played_appid": most_played_game.get("appid") if most_played_game else None,
            "total_games": len(games),
            "never_played_count": len(never_played),
            "never_played_percent": round((len(never_played) / len(games)) * 100) if games else 0,
            "total_hours": total_hours,
            "top_games": top_games,
            "most_played": top_games[0] if top_games else None,
            "recently_played": recently_played,
        }

    except Exception as e:
        print("Steam fetch error:", e)
        return {"error": str(e)}