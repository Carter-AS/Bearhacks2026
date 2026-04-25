import requests

RIOT_API_KEY = "RGAPI-f56c33fb-c44a-4147-bd5b-24040ca18bd8"
STEAM_API_KEY = "85B394EA9E17DCF0365A60AC4B43BDC9"
RIOT_REGION = "na1"  # change to euw1, kr, etc. if needed

# ── Riot Data ─────────────────────────────────────────────────

def fetch_riot_data(username: str) -> dict:
    try:
        # Username format: "Name#TAG"
        if "#" in username:
            game_name, tag_line = username.split("#", 1)
        else:
            game_name, tag_line = username, "NA1"

        # 1. Get PUUID from Riot account
        account_url = (
            f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id"
            f"/{game_name}/{tag_line}?api_key={RIOT_API_KEY}"
        )
        account_response = requests.get(account_url)
        print("Riot API status:", account_response.status_code)
        print("Riot API response:", account_response.text)
        account = account_response.json()
        puuid = account.get("puuid")

        if not puuid:
            return {"error": "Riot user not found"}

        # 2. Get summoner data
        summoner_url = (
            f"https://{RIOT_REGION}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid"
            f"/{puuid}?api_key={RIOT_API_KEY}"
        )
        summoner_response = requests.get(summoner_url)
        print("Summoner API status:", summoner_response.status_code)
        print("Summoner API response:", summoner_response.text)
        summoner = summoner_response.json()

        summoner_level = summoner.get("summonerLevel", 0)

        # 3. Get ranked stats (using puuid now — Riot removed summoner id)
        ranked_url = (
            f"https://{RIOT_REGION}.api.riotgames.com/lol/league/v4/entries/by-puuid"
            f"/{puuid}?api_key={RIOT_API_KEY}"
        )       
        ranked_data = requests.get(ranked_url).json()

        rank_info = {}
        for entry in ranked_data:
            if entry.get("queueType") == "RANKED_SOLO_5x5":
                wins = entry.get("wins", 0)
                losses = entry.get("losses", 0)
                total = wins + losses
                rank_info = {
                    "tier": entry.get("tier", "UNRANKED"),
                    "rank": entry.get("rank", ""),
                    "lp": entry.get("leaguePoints", 0),
                    "wins": wins,
                    "losses": losses,
                    "total_games": total,
                    "win_rate": round((wins / total) * 100) if total > 0 else 0,
                }

        # 4. Get match history (last 20 games)
        matches_url = (
            f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid"
            f"/{puuid}/ids?start=0&count=20&api_key={RIOT_API_KEY}"
        )
        match_ids = requests.get(matches_url).json()

        total_deaths = 0
        total_kills = 0
        total_assists = 0
        champion_counts = {}
        vision_scores = []

        for match_id in match_ids[:10]:  # limit to 10 to avoid rate limit
            match_url = (
                f"https://americas.api.riotgames.com/lol/match/v5/matches"
                f"/{match_id}?api_key={RIOT_API_KEY}"
            )
            match = requests.get(match_url).json()
            participants = match.get("info", {}).get("participants", [])

            for p in participants:
                if p.get("puuid") == puuid:
                    total_deaths += p.get("deaths", 0)
                    total_kills += p.get("kills", 0)
                    total_assists += p.get("assists", 0)
                    vision_scores.append(p.get("visionScore", 0))
                    champ = p.get("championName", "Unknown")
                    champion_counts[champ] = champion_counts.get(champ, 0) + 1

        avg_vision = round(sum(vision_scores) / len(vision_scores)) if vision_scores else 0
        top_champions = sorted(champion_counts, key=champion_counts.get, reverse=True)[:3]

        return {
            "username": username,
            "summoner_level": summoner_level,
            "rank": rank_info,
            "recent_stats": {
                "total_deaths": total_deaths,
                "total_kills": total_kills,
                "total_assists": total_assists,
                "avg_vision_score": avg_vision,
                "kda": round((total_kills + total_assists) / max(total_deaths, 1), 2),
            },
            "top_champions": top_champions,
        }

    except Exception as e:
        return {"error": str(e)}


# ── Steam Data ────────────────────────────────────────────────

def fetch_steam_data(username: str) -> dict:
    try:
        # 1. Resolve username to Steam ID
        resolve_url = (
            f"https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/"
            f"?key={STEAM_API_KEY}&vanityurl={username}"
        )
        resolve = requests.get(resolve_url).json()
        steam_id = resolve.get("response", {}).get("steamid")

        if not steam_id:
            return {"error": "Steam user not found"}

        # 2. Get profile info
        profile_url = (
            f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/"
            f"?key={STEAM_API_KEY}&steamids={steam_id}"
        )
        profile_data = requests.get(profile_url).json()
        player = profile_data.get("response", {}).get("players", [{}])[0]

        # 3. Get owned games
        games_url = (
            f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v1/"
            f"?key={STEAM_API_KEY}&steamid={steam_id}&include_appinfo=true&include_played_free_games=true"
        )
        games_data = requests.get(games_url).json()
        games = games_data.get("response", {}).get("games", [])

        total_games = len(games)
        never_played = [g for g in games if g.get("playtime_forever", 0) == 0]
        played_games = [g for g in games if g.get("playtime_forever", 0) > 0]
        played_games_sorted = sorted(played_games, key=lambda g: g.get("playtime_forever", 0), reverse=True)

        top_games = [
            {
                "name": g.get("name", "Unknown"),
                "hours": round(g.get("playtime_forever", 0) / 60),
            }
            for g in played_games_sorted[:5]
        ]

        total_hours = round(sum(g.get("playtime_forever", 0) for g in games) / 60)

        return {
            "username": player.get("personaname", username),
            "steam_id": steam_id,
            "avatar": player.get("avatarfull"),
            "profile_url": player.get("profileurl"),
            "total_games": total_games,
            "never_played": len(never_played),
            "total_hours": total_hours,
            "top_games": top_games,
            "most_played": top_games[0] if top_games else None,
        }

    except Exception as e:
        return {"error": str(e)}