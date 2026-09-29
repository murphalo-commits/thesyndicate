import os
import sys
import json
import time
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
import urllib.request
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

def format_to_eastern(iso_str):
    """Converts an ISO 8601 UTC timestamp string to US Eastern Time (YYYY-MM-DD HH:MM:SS)."""
    if not iso_str:
        return ""
    try:
        clean_iso = iso_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean_iso)
        try:
            dt_eastern = dt.astimezone(ZoneInfo("America/New_York"))
        except Exception:
            dt_eastern = dt.astimezone(timezone(timedelta(hours=-4)))
        return dt_eastern.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return iso_str.replace("T", " ").replace("Z", "")

# Google Sheets Config
CREDENTIALS_FILE = "credentials.json"
SPREADSHEET_ID = "1V03afDSY0tWIbqQAJhOcuv2A13Z9eJoi0XKs9zoc7Nk"

# APIs
NOVIG_GQL_URL = "https://api.novig.us/v1/graphql"
ODDS_API_BASE = "https://api.the-odds-api.com/v4"

# Player Prop Markets supported per sport
PROP_MARKETS = {
    "americanfootball_nfl": [
        "player_pass_tds", "player_pass_yds", "player_pass_completions",
        "player_rush_yds", "player_rush_attempts",
        "player_reception_yds", "player_receptions", "player_anytime_td"
    ],
    "americanfootball_ncaaf": [
        "player_pass_tds", "player_pass_yds", "player_rush_yds",
        "player_reception_yds", "player_anytime_td"
    ],
    "baseball_mlb": [
        "pitcher_strikeouts", "batter_hits", "batter_total_bases",
        "batter_home_runs", "batter_rbis"
    ],
    "basketball_nba": [
        "player_points", "player_rebounds", "player_assists",
        "player_threes", "player_points_rebounds_assists"
    ],
    "basketball_wnba": [
        "player_points", "player_rebounds", "player_assists", "player_threes"
    ],
    "icehockey_nhl": [
        "player_points", "player_goals", "player_assists", "player_shots_on_goal"
    ]
}

MARKET_LABELS = {
    "player_pass_tds": "Passing Touchdowns",
    "player_pass_yds": "Passing Yards",
    "player_pass_completions": "Pass Completions",
    "player_rush_yds": "Rushing Yards",
    "player_rush_attempts": "Rushing Attempts",
    "player_reception_yds": "Receiving Yards",
    "player_receptions": "Receptions",
    "player_anytime_td": "Anytime Touchdown",
    "pitcher_strikeouts": "Strikeouts",
    "batter_hits": "Hits",
    "batter_total_bases": "Total Bases",
    "batter_home_runs": "Home Runs",
    "batter_rbis": "RBIs",
    "player_points": "Points",
    "player_rebounds": "Rebounds",
    "player_assists": "Assists",
    "player_threes": "Three Pointers",
    "player_points_rebounds_assists": "Pts + Reb + Ast",
    "player_goals": "Goals",
    "player_shots_on_goal": "Shots on Goal"
}

PROPS_SPORT_CONFIG = [
    ("Props - NFL (americanfootball_nfl)", "americanfootball_nfl", "TRUE"),
    ("Props - NCAAF (americanfootball_ncaaf)", "americanfootball_ncaaf", "FALSE"),
    ("Props - MLB (baseball_mlb)", "baseball_mlb", "TRUE"),
    ("Props - NBA (basketball_nba)", "basketball_nba", "FALSE"),
    ("Props - WNBA (basketball_wnba)", "basketball_wnba", "FALSE"),
    ("Props - NHL (icehockey_nhl)", "icehockey_nhl", "FALSE"),
]

def get_google_sheet():
    """Connects to Google Sheets using service account credentials from file or GOOGLE_CREDENTIALS env var."""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = None

    if os.path.exists(CREDENTIALS_FILE):
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
    elif os.environ.get("GOOGLE_CREDENTIALS"):
        try:
            creds_dict = json.loads(os.environ["GOOGLE_CREDENTIALS"])
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        except Exception as e:
            print(f"Error parsing GOOGLE_CREDENTIALS environment variable: {e}")
            sys.exit(1)
    else:
        print(f"Error: '{CREDENTIALS_FILE}' not found and GOOGLE_CREDENTIALS env var not set.")
        print("Please follow setup instructions or set GOOGLE_CREDENTIALS in your GitHub repository secrets.")
        sys.exit(1)

    client = gspread.authorize(creds)
    
    try:
        sheet = client.open_by_key(SPREADSHEET_ID)
        return sheet
    except gspread.exceptions.SpreadsheetNotFound:
        print(f"Error: Google Sheet with ID '{SPREADSHEET_ID}' not found.")
        print("Make sure you have shared the sheet with the Service Account email address.")
        sys.exit(1)

def ensure_settings_rows(settings_sheet):
    """Ensures player props settings exist in Settings tab."""
    try:
        records = settings_sheet.col_values(1)
        keys = [r.strip() for r in records]
        
        status_idx = None
        for i, k in enumerate(keys, start=1):
            if "STATUS" in k:
                status_idx = i
                break
                
        if "--- PLAYER PROPS (SPORT SELECTOR) ---" not in keys:
            target_idx = status_idx
            if "Fetch Player Props" in keys:
                target_idx = keys.index("Fetch Player Props") + 1
            if target_idx:
                settings_sheet.insert_row(["--- PLAYER PROPS (SPORT SELECTOR) ---", ""], index=target_idx)
                if status_idx and target_idx <= status_idx:
                    status_idx += 1
            else:
                settings_sheet.append_row(["--- PLAYER PROPS (SPORT SELECTOR) ---", ""])
                
        records = settings_sheet.col_values(1)
        keys = [r.strip() for r in records]
        for i, k in enumerate(keys, start=1):
            if "STATUS" in k:
                status_idx = i
                break

        if "Fetch Player Props" not in keys:
            if status_idx:
                settings_sheet.insert_row(["Fetch Player Props", "TRUE"], index=status_idx)
                status_idx += 1
            else:
                settings_sheet.append_row(["Fetch Player Props", "TRUE"])
                
        if "Props Time Horizon (Hours)" not in keys:
            if status_idx:
                settings_sheet.insert_row(["Props Time Horizon (Hours)", "36"], index=status_idx)
                status_idx += 1
            else:
                settings_sheet.append_row(["Props Time Horizon (Hours)", "36"])
                
        for label, _, default_val in PROPS_SPORT_CONFIG:
            if label not in keys:
                if status_idx:
                    settings_sheet.insert_row([label, default_val], index=status_idx)
                    status_idx += 1
                else:
                    settings_sheet.append_row([label, default_val])
    except Exception as e:
        print("Warning: Could not check/insert settings rows:", e)

def read_settings(settings_sheet):
    """Reads settings key-values dynamically from the Settings tab."""
    records = settings_sheet.get_all_values()
    settings = {}
    for row in records:
        if len(row) >= 2 and row[0].strip():
            key = row[0].strip()
            val = row[1].strip()
            # Convert true/false strings to booleans
            if val.lower() == "true":
                settings[key] = True
            elif val.lower() == "false":
                settings[key] = False
            else:
                settings[key] = val
    return settings

def update_status(settings_sheet, message):
    """Updates the status timestamp and message in the Settings tab."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    labels = settings_sheet.col_values(1)
    
    last_updated_row = None
    status_msg_row = None
    
    for idx, label in enumerate(labels, start=1):
        if label.strip() == "Last Updated":
            last_updated_row = idx
        elif label.strip() == "Status Message":
            status_msg_row = idx
            
    if last_updated_row:
        settings_sheet.update_cell(last_updated_row, 2, timestamp)
    if status_msg_row:
        settings_sheet.update_cell(status_msg_row, 2, message)

def map_sport_to_novig_league(sport_key):
    """Maps standard sport keys to Novig's internal league codes."""
    sk = sport_key.lower()
    if "nfl" in sk: return ["NFL"]
    if "ncaaf" in sk: return ["NCAAF"]
    if "nba" in sk: return ["NBA"]
    if "ncaab" in sk: return ["NCAAB"]
    if "wnba" in sk: return ["WNBA"]
    if "wncaab" in sk: return ["NCAAW"]
    if "mlb" in sk: return ["MLB"]
    if "nhl" in sk: return ["NHL"]
    if "tennis" in sk: return ["ATP", "WTA"]
    return []

def get_active_tennis_sports(api_key):
    """Queries active tennis tournament keys from The Odds API (free call)."""
    url = f"{ODDS_API_BASE}/sports/?apiKey={api_key}"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req) as res:
            sports = json.loads(res.read().decode("utf-8"))
            return [s["key"] for s in sports if s["key"].startswith("tennis_")]
    except Exception as e:
        print("Warning: Failed to fetch active tennis sports:", e)
        return []

def fetch_odds_api(api_key, sports, bookmakers, odds_format):
    """Fetches lines from The Odds API for all active books and sports.
    Returns (odds_rows, events_by_sport).
    """
    odds_rows = []
    events_by_sport = {}
    
    regions = "us"
    if "novig" in bookmakers:
        regions = "us,us_ex"
        
    for sport in sports:
        print(f"Fetching {sport} from The Odds API...")
        url = (
            f"{ODDS_API_BASE}/sports/{sport}/odds/"
            f"?apiKey={api_key}&regions={regions}&markets=h2h,spreads,totals"
            f"&oddsFormat={odds_format}&bookmakers={','.join(bookmakers)}"
        )
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req) as res:
                events = json.loads(res.read().decode("utf-8"))
                events_by_sport[sport] = events
                for event in events:
                    event_id = event["id"]
                    sport_title = event["sport_title"]
                    commence_time = event["commence_time"]
                    home_team = event["home_team"]
                    away_team = event["away_team"]
                    
                    for book in event.get("bookmakers", []):
                        book_title = book["title"]
                        last_update = book["last_update"]
                        
                        for market in book.get("markets", []):
                            market_key = market["key"]
                            for outcome in market.get("outcomes", []):
                                name = outcome["name"]
                                price = outcome["price"]
                                point = outcome.get("point", "")
                                formatted_commence = format_to_eastern(commence_time)
                                formatted_update = format_to_eastern(last_update)
                                odds_rows.append([
                                    event_id, sport_title, formatted_commence,
                                    home_team, away_team, book_title,
                                    market_key, name, point, price, formatted_update
                                ])
        except Exception as e:
            print(f"Error fetching {sport} from The Odds API: {e}")
            
    return odds_rows, events_by_sport

def fetch_player_props(api_key, events_by_sport, bookmakers, odds_format, horizon_hours=36, allowed_sports=None):
    """Fetches player props from The Odds API for games scheduled within horizon_hours for allowed sports."""
    props_rows = []
    now_utc = datetime.now(timezone.utc)
    cutoff_utc = now_utc + timedelta(hours=horizon_hours)
    
    regions = "us"
    if "novig" in bookmakers:
        regions = "us,us_ex"
        
    for sport, events in events_by_sport.items():
        if sport not in PROP_MARKETS:
            continue
            
        if allowed_sports is not None and sport not in allowed_sports:
            continue
            
        markets = PROP_MARKETS[sport]
        markets_str = ",".join(markets)
        
        for event in events:
            # Filter games by commence time
            try:
                ev_time_str = event["commence_time"].replace("Z", "+00:00")
                ev_dt = datetime.fromisoformat(ev_time_str)
                # Include games from 4 hours ago (in-game/recent) up to horizon_hours into future
                if not (now_utc - timedelta(hours=4) <= ev_dt <= cutoff_utc):
                    continue
            except Exception:
                pass
                
            eid = event["id"]
            away = event["away_team"]
            home = event["home_team"]
            matchup = f"{away} @ {home}"
            sport_title = event.get("sport_title", sport)
            commence_time = event["commence_time"]
            
            print(f"Fetching props for {matchup} ({sport_title})...")
            url = (
                f"{ODDS_API_BASE}/sports/{sport}/events/{eid}/odds"
                f"?apiKey={api_key}&regions={regions}&markets={markets_str}"
                f"&oddsFormat={odds_format}&bookmakers={','.join(bookmakers)}"
            )
            try:
                req = urllib.request.Request(url, method="GET")
                with urllib.request.urlopen(req) as res:
                    data = json.loads(res.read().decode("utf-8"))
                    for book in data.get("bookmakers", []):
                        b_title = book.get("title", "")
                        for market in book.get("markets", []):
                            m_key = market.get("key", "")
                            m_label = MARKET_LABELS.get(m_key, m_key)
                            last_update = market.get("last_update", "")
                            for outcome in market.get("outcomes", []):
                                p_name = outcome.get("description", "")
                                o_name = outcome.get("name", "")
                                line = outcome.get("point", "")
                                price = outcome.get("price", "")
                                if not p_name and o_name:
                                    p_name = o_name
                                    o_name = "Yes"
                                    
                                formatted_commence = format_to_eastern(commence_time)
                                formatted_update = format_to_eastern(last_update)
                                props_rows.append([
                                    eid, sport_title, formatted_commence, matchup,
                                    p_name, m_label, o_name, line, b_title, price, formatted_update
                                ])
            except Exception as e:
                print(f"Error fetching props for {matchup}: {e}")
                
            time.sleep(0.1)
            
    return props_rows

def prob_to_american(prob, format_type="american"):
    """Converts a decimal probability to American or standard decimal odds."""
    if not prob or prob <= 0 or prob >= 1:
        return ""
    if format_type == "decimal":
        return round(1 / prob, 2)
    # American format
    if prob > 0.5:
        return int(round(-(prob / (1 - prob)) * 100))
    else:
        return int(round(((1 - prob) / prob) * 100))

def post_gql(query_data, max_retries=3, backoff=2):
    """Sends a POST request to Novig's public GraphQL endpoint with retry logic."""
    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(
                NOVIG_GQL_URL, 
                data=json.dumps(query_data).encode("utf-8"), 
                headers={
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
                }, 
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=15) as res:
                return json.loads(res.read().decode("utf-8"))
        except Exception as e:
            if attempt < max_retries:
                print(f"Warning: Novig GraphQL attempt {attempt}/{max_retries} failed: {e}. Retrying in {backoff * attempt}s...")
                time.sleep(backoff * attempt)
            else:
                raise e

def classify_outcome(event_name, market_type, o_desc, competitor_name):
    """Classifies an outcome dynamically as Home, Away, Over, or Under based on name patterns."""
    o_lower = o_desc.lower()
    if market_type == "TOTAL":
        if "over" in o_lower:
            return "Over"
        elif "under" in o_lower:
            return "Under"
        return ""
        
    event_lower = event_name.lower()
    split_chars = [" @ ", " at ", " vs ", " v "]
    away_team = ""
    home_team = ""
    for char in split_chars:
        if char in event_lower:
            parts = event_lower.split(char)
            away_team = parts[0].strip()
            home_team = parts[1].strip()
            break
            
    if not away_team or not home_team:
        return ""
        
    comp_lower = competitor_name.lower() if competitor_name else o_lower
    cleaned_comp = comp_lower.split("-")[0].split("+")[0].strip()
    
    if cleaned_comp in away_team or away_team in cleaned_comp:
        return "Away"
    elif cleaned_comp in home_team or home_team in cleaned_comp:
        return "Home"
        
    # Acronym fallback (e.g. PSU -> Penn State)
    away_acronym = "".join([t[0] for t in away_team.split() if t not in ["and", "or"]])
    home_acronym = "".join([t[0] for t in home_team.split() if t not in ["and", "or"]])
    if away_acronym == cleaned_comp:
        return "Away"
    elif home_acronym == cleaned_comp:
        return "Home"
        
    return ""

def fetch_novig_depth(leagues, odds_format):
    """Fetches detailed order book depth by splitting metadata and orders to avoid timeouts.
    Uses two-outcome cross-matching logic to resolve backing/laying odds from one-sided bids database.
    """
    metadata_query = {
        "query": """
        query GetMetadata($leagues: [String!]) {
          event(where: { _and: [{ status: { _in: ["OPEN_PREGAME", "OPEN_INGAME"] } }, { game: { league: { _in: $leagues } } }] }) {
            description
            game {
              league
            }
            markets(where: { type: { _in: ["SPREAD", "TOTAL", "MONEY", "MONEYLINE"] } }) {
              id
              description
              type
              strike
              outcomes {
                id
                description
                competitor {
                  name
                }
              }
            }
          }
        }
        """,
        "variables": {
            "leagues": leagues
        }
    }
    
    orders_query = {
        "query": """
        query GetActiveOrders {
          order(where: { status: { _eq: "OPEN" } }) {
            outcome_id
            price
            qty
            isBid
          }
        }
        """
    }
    
    depth_rows = []
    try:
        print("Querying Novig GraphQL API for metadata...")
        meta_res = post_gql(metadata_query)
        if "errors" in meta_res:
            print("Error fetching Novig metadata:", meta_res["errors"])
            return []
        events = meta_res.get("data", {}).get("event", [])
        
        print("Querying Novig GraphQL API for active orders...")
        orders_res = post_gql(orders_query)
        if "errors" in orders_res:
            print("Error fetching Novig active orders:", orders_res["errors"])
            return []
        orders = orders_res.get("data", {}).get("order", [])
        
        # Build maps
        outcome_map = {}
        market_outcomes = {}
        for ev in events:
            ev_name = ev["description"]
            league = ev.get("game", {}).get("league", "")
            for m in ev.get("markets", []):
                m_id = m["id"]
                market_outcomes[m_id] = []
                for o in m.get("outcomes", []):
                    comp_name = o["competitor"]["name"] if o.get("competitor") else ""
                    outcome_obj = {
                        "id": o["id"],
                        "description": o["description"],
                        "competitor_name": comp_name,
                        "market_type": m["type"],
                        "strike": m["strike"] if m["strike"] is not None else "",
                        "event_name": ev_name,
                        "league": league
                    }
                    outcome_map[o["id"]] = outcome_obj
                    market_outcomes[m_id].append(outcome_obj)
                    
        # Group orders by outcome ID
        orders_by_outcome = {}
        for order in orders:
            o_id = order["outcome_id"]
            if o_id in outcome_map:
                if o_id not in orders_by_outcome:
                    orders_by_outcome[o_id] = []
                orders_by_outcome[o_id].append(order)
                
        def aggregate_bids(raw_orders):
            agg = {}
            for o in raw_orders:
                if not o.get("isBid"):
                    continue
                p = round(float(o["price"]), 4)
                agg[p] = agg.get(p, 0.0) + float(o["qty"])
            sorted_p = sorted(agg.keys(), reverse=True)
            return [{"price": p, "qty": agg[p], "isBid": True} for p in sorted_p]

        # Generate cross-matched back/lay depth levels
        for m_id, outcomes in market_outcomes.items():
            if len(outcomes) != 2:
                continue  # Only handle standard two-outcome markets
                
            out_A = outcomes[0]
            out_B = outcomes[1]
            
            orders_A = orders_by_outcome.get(out_A["id"], [])
            orders_B = orders_by_outcome.get(out_B["id"], [])
            
            bids_A = aggregate_bids(orders_A)
            bids_B = aggregate_bids(orders_B)
            
            # Dynamically classify outcomes as Home, Away, Over, or Under
            class_A = classify_outcome(out_A["event_name"], out_A["market_type"], out_A["description"], out_A["competitor_name"])
            class_B = classify_outcome(out_B["event_name"], out_B["market_type"], out_B["description"], out_B["competitor_name"])
            
            # --- OUTCOME A ---
            # 1. Backing A (matches Bids on B)
            for idx, bid in enumerate(bids_B[:3]):
                back_price = 1 - bid["price"]
                odds = prob_to_american(back_price, odds_format)
                max_bet_risk = (bid["qty"] / 100) * back_price
                depth_rows.append([
                    out_A["event_name"], out_A["league"], out_A["market_type"], out_A["description"],
                    out_A["strike"], "Back", odds, round(max_bet_risk, 2), idx + 1, class_A
                ])
            # 2. Laying A (matches Bids on A)
            for idx, bid in enumerate(bids_A[:3]):
                lay_price = bid["price"]
                odds = prob_to_american(lay_price, odds_format)
                max_bet_risk = (bid["qty"] / 100) * (1 - lay_price)
                depth_rows.append([
                    out_A["event_name"], out_A["league"], out_A["market_type"], out_A["description"],
                    out_A["strike"], "Lay", odds, round(max_bet_risk, 2), idx + 1, class_A
                ])
                
            # --- OUTCOME B ---
            # 3. Backing B (matches Bids on A)
            for idx, bid in enumerate(bids_A[:3]):
                back_price = 1 - bid["price"]
                odds = prob_to_american(back_price, odds_format)
                max_bet_risk = (bid["qty"] / 100) * back_price
                depth_rows.append([
                    out_B["event_name"], out_B["league"], out_B["market_type"], out_B["description"],
                    out_B["strike"], "Back", odds, round(max_bet_risk, 2), idx + 1, class_B
                ])
            # 4. Laying B (matches Bids on B)
            for idx, bid in enumerate(bids_B[:3]):
                lay_price = bid["price"]
                odds = prob_to_american(lay_price, odds_format)
                max_bet_risk = (bid["qty"] / 100) * (1 - lay_price)
                depth_rows.append([
                    out_B["event_name"], out_B["league"], out_B["market_type"], out_B["description"],
                    out_B["strike"], "Lay", odds, round(max_bet_risk, 2), idx + 1, class_B
                ])
                
    except Exception as e:
        print("Error fetching detailed Novig depth:", e)
        
    return depth_rows

def find_novig_quote(home_team, away_team, market_key, outcome_name, point, depth_data):
    """Matches an outcome row to its corresponding Level 1 Back odds and liquidity from Novig GQL depth."""
    if not depth_data:
        return None, ""
        
    target_types = []
    if market_key == "h2h":
        target_types = ["MONEY", "MONEYLINE"]
    elif market_key == "spreads":
        target_types = ["SPREAD"]
    elif market_key == "totals":
        target_types = ["TOTAL"]
        
    home_lower = home_team.lower()
    away_lower = away_team.lower()
    out_lower = outcome_name.lower()
    
    is_home = (out_lower in home_lower or home_lower in out_lower)
    is_away = (out_lower in away_lower or away_lower in out_lower)
    
    home_words = set(w for w in home_lower.split() if len(w) > 3 and w not in ["state", "university"])
    away_words = set(w for w in away_lower.split() if len(w) > 3 and w not in ["state", "university"])
    
    for row in depth_data:
        # Row layout: [event_name, league, market_type, outcome_name, strike, side, odds, max_bet_risk, depth_level, outcome_class]
        ev_name, _, m_type, o_name, strike, side, odds, max_bet_risk, depth_level, o_class = row
        
        # We only want the best Back liquidity (Level 1)
        if side != "Back" or str(depth_level) != "1":
            continue
            
        if m_type not in target_types:
            continue
            
        # Check event name matches (BOTH home and away teams must be represented)
        ev_lower = ev_name.lower()
        ev_words = set(ev_lower.split())
        has_home = (home_lower in ev_lower) or bool(home_words.intersection(ev_words))
        has_away = (away_lower in ev_lower) or bool(away_words.intersection(ev_words))
        if not (has_home and has_away):
            continue
            
        # Match by market
        if market_key == "h2h":
            if is_home and o_class == "Home":
                return odds, max_bet_risk
            if is_away and o_class == "Away":
                return odds, max_bet_risk
            # Fallback on outcome name matching if classification wasn't Home/Away
            cleaned_o_name = o_name.lower().split("-")[0].split("+")[0].strip()
            if is_home and (cleaned_o_name in home_lower or home_lower in cleaned_o_name):
                return odds, max_bet_risk
            if is_away and (cleaned_o_name in away_lower or away_lower in cleaned_o_name):
                return odds, max_bet_risk
                
        elif market_key == "spreads":
            try:
                pt_val = float(point)
                stk_val = float(strike)
                # If Home, point should equal strike. If Away, point should equal -strike.
                if is_home and o_class == "Home" and abs(pt_val - stk_val) < 0.01:
                    return odds, max_bet_risk
                if is_away and o_class == "Away" and abs(pt_val - (-stk_val)) < 0.01:
                    return odds, max_bet_risk
            except Exception:
                pass
                
        elif market_key == "totals":
            try:
                pt_val = float(point)
                stk_val = float(strike)
                if abs(pt_val - stk_val) < 0.01:
                    if "over" in out_lower and o_class == "Over":
                        return odds, max_bet_risk
                    if "under" in out_lower and o_class == "Under":
                        return odds, max_bet_risk
            except Exception:
                pass
                
def export_mobile_data(odds_data_with_liq, props_data):
    """Exports lightweight JSON bundle for mobile web app."""
    try:
        def american_to_implied(price):
            try:
                p = float(price)
                if p > 0:
                    return 100.0 / (p + 100.0)
                elif p < 0:
                    return abs(p) / (abs(p) + 100.0)
            except Exception:
                pass
            return 0.5

        def sport_to_label(s):
            s_lower = str(s).lower()
            if "wnba" in s_lower: return "WNBA"
            if "ncaaf" in s_lower: return "NCAAF"
            if "ncaab" in s_lower: return "NCAAB"
            if "nfl" in s_lower: return "NFL"
            if "mlb" in s_lower or "baseball" in s_lower: return "MLB"
            if "nhl" in s_lower or "hockey" in s_lower: return "NHL"
            if "nba" in s_lower or "basketball" in s_lower: return "NBA"
            return s.upper()

        def get_team_abbr(name):
            special = {
                "Philadelphia Eagles": "PHI", "Chicago Bears": "CHI",
                "San Diego State Aztecs": "SDSU", "James Madison Dukes": "JMU",
                "Boise State Broncos": "BSU", "San Diego Toreros": "USD",
                "Northern Illinois Huskies": "NIU", "Arizona Wildcats": "ARIZ",
                # WNBA
                "Las Vegas Aces": "LVA", "Indiana Fever": "IND",
                "Minnesota Lynx": "MIN", "New York Liberty": "NYL",
                "Atlanta Dream": "ATL", "Washington Mystics": "WAS",
                "Golden State Valkyries": "GSV", "Dallas Wings": "DAL",
                "Chicago Sky": "CHI", "Connecticut Sun": "CON",
                "Los Angeles Sparks": "LAS", "Phoenix Mercury": "PHX",
                "Seattle Storm": "SEA"
            }
            if name in special:
                return special[name]
            tokens = name.split()
            return tokens[-1][:3].upper() if tokens else name[:3].upper()

        events = {}
        for row in odds_data_with_liq:
            eid, sport, commence, home, away, book, market, outcome, point, price, _, liq = row
            try:
                price_val = float(price)
            except Exception:
                continue

            if eid not in events:
                events[eid] = {
                    "id": eid,
                    "sport": sport,
                    "sport_label": sport_to_label(sport),
                    "home_team": home,
                    "away_team": away,
                    "home_abbr": get_team_abbr(home),
                    "away_abbr": get_team_abbr(away),
                    "commence_time": commence,
                    "markets": {"h2h": {}, "spreads": {}, "totals": {}}
                }

            ev = events[eid]
            m_key = "h2h" if market in ["h2h", "moneyline", "money"] else ("spreads" if market in ["spreads", "spread"] else ("totals" if market in ["totals", "total"] else None))
            if not m_key: continue

            if book not in ev["markets"][m_key]:
                ev["markets"][m_key][book] = []

            ev["markets"][m_key][book].append({
                "outcome": outcome,
                "point": point,
                "price": price_val,
                "liquidity": float(liq) if liq and str(liq).replace('.','').isdigit() else 0
            })

        matchups_list = []
        arbs_list = []

        for eid, ev in events.items():
            home = ev["home_team"]
            away = ev["away_team"]

            # Moneyline: Overall, Retail-only, and Novig-only
            best_ml_home, best_ml_away = None, None
            best_retail_ml_home, best_retail_ml_away = None, None
            novig_ml_home, novig_ml_away = None, None

            for book, rows in ev["markets"]["h2h"].items():
                is_novig = (book.lower() == "novig")
                for r in rows:
                    entry = {"book": book, "price": r["price"], "liquidity": r["liquidity"]}
                    if r["outcome"] == home:
                        if best_ml_home is None or r["price"] > best_ml_home["price"]:
                            best_ml_home = entry
                        if is_novig:
                            if novig_ml_home is None or r["price"] > novig_ml_home["price"]:
                                novig_ml_home = entry
                        else:
                            if best_retail_ml_home is None or r["price"] > best_retail_ml_home["price"]:
                                best_retail_ml_home = entry
                    elif r["outcome"] == away:
                        if best_ml_away is None or r["price"] > best_ml_away["price"]:
                            best_ml_away = entry
                        if is_novig:
                            if novig_ml_away is None or r["price"] > novig_ml_away["price"]:
                                novig_ml_away = entry
                        else:
                            if best_retail_ml_away is None or r["price"] > best_retail_ml_away["price"]:
                                best_retail_ml_away = entry

            # Moneyline: Overall best
            best_ml_away = novig_ml_away if (novig_ml_away and (not best_retail_ml_away or novig_ml_away["price"] > best_retail_ml_away["price"])) else best_retail_ml_away
            best_ml_home = novig_ml_home if (novig_ml_home and (not best_retail_ml_home or novig_ml_home["price"] > best_retail_ml_home["price"])) else best_retail_ml_home

            # Moneyline Arbs: Novig can only be ONE side of the bet!
            ml_pairs = [
                (best_retail_ml_away, best_retail_ml_home, f"arb_ml_{eid}_ret"),
                (best_retail_ml_away, novig_ml_home, f"arb_ml_{eid}_ret_nov"),
                (novig_ml_away, best_retail_ml_home, f"arb_ml_{eid}_nov_ret")
            ]
            for s_a, s_b, arb_id in ml_pairs:
                if s_a and s_b:
                    tot_imp = american_to_implied(s_a["price"]) + american_to_implied(s_b["price"])
                    if tot_imp < 1.015:
                        roi = round((1.0 - tot_imp) * 100, 2)
                        has_novig = (s_a["book"].lower() == "novig" or s_b["book"].lower() == "novig")
                        arbs_list.append({
                            "id": arb_id,
                            "sport": ev["sport_label"],
                            "matchup": f"{away} @ {home}",
                            "market": "Moneyline",
                            "roi": roi,
                            "hold": round(tot_imp * 100, 2),
                            "commence_time": ev["commence_time"],
                            "is_novig": has_novig,
                            "side_a": {"name": away, "outcome": f"{away} ML", "book": s_a["book"], "price": s_a["price"], "liquidity": s_a["liquidity"]},
                            "side_b": {"name": home, "outcome": f"{home} ML", "book": s_b["book"], "price": s_b["price"], "liquidity": s_b["liquidity"]}
                        })

            # Spreads: Bucket by target home point so away point is strictly opposite (-point)
            spread_buckets = {}
            for book, rows in ev["markets"]["spreads"].items():
                is_novig = (book.lower() == "novig")
                for r in rows:
                    pt = r.get("point")
                    if pt is None or pt == "": continue
                    try:
                        pt_val = float(pt)
                    except Exception:
                        continue
                    is_home = (r["outcome"] == home)
                    target_home_pt = pt_val if is_home else -pt_val
                    if target_home_pt not in spread_buckets:
                        spread_buckets[target_home_pt] = {"retail_home": [], "retail_away": [], "novig_home": [], "novig_away": []}
                    entry = {"book": book, "point": pt_val, "price": r["price"], "liquidity": r["liquidity"]}
                    if is_home:
                        if is_novig: spread_buckets[target_home_pt]["novig_home"].append(entry)
                        else: spread_buckets[target_home_pt]["retail_home"].append(entry)
                    else:
                        if is_novig: spread_buckets[target_home_pt]["novig_away"].append(entry)
                        else: spread_buckets[target_home_pt]["retail_away"].append(entry)

            best_spread_home, best_spread_away = None, None
            best_retail_spread_home, best_retail_spread_away = None, None
            novig_spread_home, novig_spread_away = None, None
            lowest_spd_hold = 999.0

            for h_pt, bucket in spread_buckets.items():
                ret_h = max(bucket["retail_home"], key=lambda x: x["price"]) if bucket["retail_home"] else None
                ret_a = max(bucket["retail_away"], key=lambda x: x["price"]) if bucket["retail_away"] else None
                nov_h = max(bucket["novig_home"], key=lambda x: x["price"]) if bucket["novig_home"] else None
                nov_a = max(bucket["novig_away"], key=lambda x: x["price"]) if bucket["novig_away"] else None

                # For matchup display: pick the spread line with the tightest market hold
                cur_best_h = nov_h if (nov_h and (not ret_h or nov_h["price"] > ret_h["price"])) else ret_h
                cur_best_a = nov_a if (nov_a and (not ret_a or nov_a["price"] > ret_a["price"])) else ret_a
                if cur_best_h and cur_best_a:
                    cur_hold = american_to_implied(cur_best_h["price"]) + american_to_implied(cur_best_a["price"])
                    if cur_hold < lowest_spd_hold:
                        lowest_spd_hold = cur_hold
                        best_spread_home = cur_best_h
                        best_spread_away = cur_best_a
                        best_retail_spread_home = ret_h
                        best_retail_spread_away = ret_a
                        novig_spread_home = nov_h
                        novig_spread_away = nov_a

                # Spread Arbs: Novig can only be ONE side of the bet!
                spd_pairs = [
                    (ret_a, ret_h, f"arb_spd_{eid}_{h_pt}_ret"),
                    (ret_a, nov_h, f"arb_spd_{eid}_{h_pt}_ret_nov"),
                    (nov_a, ret_h, f"arb_spd_{eid}_{h_pt}_nov_ret")
                ]
                for s_a, s_b, arb_id in spd_pairs:
                    if s_a and s_b and (round(s_a["point"] + s_b["point"], 2) == 0):
                        tot_imp = american_to_implied(s_a["price"]) + american_to_implied(s_b["price"])
                        if tot_imp < 1.015:
                            roi = round((1.0 - tot_imp) * 100, 2)
                            has_novig = (s_a["book"].lower() == "novig" or s_b["book"].lower() == "novig")
                            pt_a_str = f"{s_a['point']:+g}"
                            pt_b_str = f"{s_b['point']:+g}"
                            display_pt = abs(h_pt)
                            arbs_list.append({
                                "id": arb_id,
                                "sport": ev["sport_label"],
                                "matchup": f"{away} @ {home}",
                                "market": f"Spread ({display_pt:g})",
                                "roi": roi,
                                "hold": round(tot_imp * 100, 2),
                                "commence_time": ev["commence_time"],
                                "is_novig": has_novig,
                                "side_a": {"name": away, "outcome": f"{away} {pt_a_str}", "book": s_a["book"], "price": s_a["price"], "liquidity": s_a["liquidity"]},
                                "side_b": {"name": home, "outcome": f"{home} {pt_b_str}", "book": s_b["book"], "price": s_b["price"], "liquidity": s_b["liquidity"]}
                            })

            # Totals: Bucket by total point
            total_buckets = {}
            for book, rows in ev["markets"]["totals"].items():
                is_novig = (book.lower() == "novig")
                for r in rows:
                    pt = r.get("point")
                    if pt is None or pt == "": continue
                    try:
                        pt_val = float(pt)
                    except Exception:
                        continue
                    if pt_val not in total_buckets:
                        total_buckets[pt_val] = {"retail_over": [], "retail_under": [], "novig_over": [], "novig_under": []}
                    entry = {"book": book, "point": pt_val, "price": r["price"], "liquidity": r["liquidity"]}
                    if r["outcome"].lower() == "over":
                        if is_novig: total_buckets[pt_val]["novig_over"].append(entry)
                        else: total_buckets[pt_val]["retail_over"].append(entry)
                    elif r["outcome"].lower() == "under":
                        if is_novig: total_buckets[pt_val]["novig_under"].append(entry)
                        else: total_buckets[pt_val]["retail_under"].append(entry)

            best_total_over, best_total_under = None, None
            best_retail_total_over, best_retail_total_under = None, None
            novig_total_over, novig_total_under = None, None
            lowest_tot_hold = 999.0

            for pt, bucket in total_buckets.items():
                ret_o = max(bucket["retail_over"], key=lambda x: x["price"]) if bucket["retail_over"] else None
                ret_u = max(bucket["retail_under"], key=lambda x: x["price"]) if bucket["retail_under"] else None
                nov_o = max(bucket["novig_over"], key=lambda x: x["price"]) if bucket["novig_over"] else None
                nov_u = max(bucket["novig_under"], key=lambda x: x["price"]) if bucket["novig_under"] else None

                # For matchup display: pick the total line with the tightest market hold
                cur_best_o = nov_o if (nov_o and (not ret_o or nov_o["price"] > ret_o["price"])) else ret_o
                cur_best_u = nov_u if (nov_u and (not ret_u or nov_u["price"] > ret_u["price"])) else ret_u
                if cur_best_o and cur_best_u:
                    cur_hold = american_to_implied(cur_best_o["price"]) + american_to_implied(cur_best_u["price"])
                    if cur_hold < lowest_tot_hold:
                        lowest_tot_hold = cur_hold
                        best_total_over = cur_best_o
                        best_total_under = cur_best_u
                        best_retail_total_over = ret_o
                        best_retail_total_under = ret_u
                        novig_total_over = nov_o
                        novig_total_under = nov_u

                # Total Arbs: Novig can only be ONE side of the bet!
                tot_pairs = [
                    (ret_o, ret_u, f"arb_tot_{eid}_{pt}_ret"),
                    (ret_o, nov_u, f"arb_tot_{eid}_{pt}_ret_nov"),
                    (nov_o, ret_u, f"arb_tot_{eid}_{pt}_nov_ret")
                ]
                for s_a, s_b, arb_id in tot_pairs:
                    if s_a and s_b:
                        tot_imp = american_to_implied(s_a["price"]) + american_to_implied(s_b["price"])
                        if tot_imp < 1.015:
                            roi = round((1.0 - tot_imp) * 100, 2)
                            has_novig = (s_a["book"].lower() == "novig" or s_b["book"].lower() == "novig")
                            arbs_list.append({
                                "id": arb_id,
                                "sport": ev["sport_label"],
                                "matchup": f"{away} @ {home}",
                                "market": f"Total ({pt:g})",
                                "roi": roi,
                                "hold": round(tot_imp * 100, 2),
                                "commence_time": ev["commence_time"],
                                "is_novig": has_novig,
                                "side_a": {"name": "Over", "outcome": f"Over {pt:g}", "book": s_a["book"], "price": s_a["price"], "liquidity": s_a["liquidity"]},
                                "side_b": {"name": "Under", "outcome": f"Under {pt:g}", "book": s_b["book"], "price": s_b["price"], "liquidity": s_b["liquidity"]}
                            })

            # Fallback if no spread/total found for matchup
            if not best_retail_spread_home and ret_h: best_retail_spread_home = ret_h
            if not best_retail_spread_away and ret_a: best_retail_spread_away = ret_a
            if not best_retail_total_over and ret_o: best_retail_total_over = ret_o
            if not best_retail_total_under and ret_u: best_retail_total_under = ret_u

            matchups_list.append({
                "id": eid,
                "sport": ev["sport"],
                "sport_label": ev["sport_label"],
                "home_team": home,
                "away_team": away,
                "home_abbr": ev["home_abbr"],
                "away_abbr": ev["away_abbr"],
                "commence_time": ev["commence_time"],
                "best_lines": {
                    "h2h_away": best_ml_away,
                    "h2h_home": best_ml_home,
                    "spread_away": best_spread_away,
                    "spread_home": best_spread_home,
                    "total_over": best_total_over,
                    "total_under": best_total_under,
                    "retail_h2h_away": best_retail_ml_away or best_ml_away,
                    "retail_h2h_home": best_retail_ml_home or best_ml_home,
                    "retail_spread_away": best_retail_spread_away or best_spread_away,
                    "retail_spread_home": best_retail_spread_home or best_spread_home,
                    "retail_total_over": best_retail_total_over or best_total_over,
                    "retail_total_under": best_retail_total_under or best_total_under,
                    "novig_h2h_away": novig_ml_away,
                    "novig_h2h_home": novig_ml_home,
                    "novig_spread_away": novig_spread_away,
                    "novig_spread_home": novig_spread_home,
                    "novig_total_over": novig_total_over,
                    "novig_total_under": novig_total_under
                },
                "all_markets": ev["markets"]
            })

        matchups_list.sort(key=lambda x: x["commence_time"])
        arbs_list.sort(key=lambda x: x["roi"], reverse=True)

        # Props
        props_list = []
        if props_data:
            df_p = pd.DataFrame(props_data, columns=["eid", "sport", "commence", "matchup", "player", "market", "outcome", "line", "book", "price", "update"])
            for (player, market, matchup), grp in df_p.groupby(["player", "market", "matchup"]):
                lines_by_book = []
                distinct_lines = set()
                for _, r in grp.iterrows():
                    try:
                        pval = float(r["price"])
                    except Exception:
                        continue
                    pt = r["line"]
                    if pt != '' and pt is not None:
                        distinct_lines.add(float(pt))
                    lines_by_book.append({"book": r["book"], "outcome": r["outcome"], "line": float(pt) if pt != '' and pt is not None else None, "price": pval})

                disc_note = f"{round(max(distinct_lines) - min(distinct_lines), 1)} line gap ({min(distinct_lines)} to {max(distinct_lines)})" if len(distinct_lines) > 1 and max(distinct_lines) > min(distinct_lines) else ""
                overs = [l for l in lines_by_book if str(l["outcome"]).lower() == "over"]
                unders = [l for l in lines_by_book if str(l["outcome"]).lower() == "under"]
                yes_tds = [l for l in lines_by_book if str(l["outcome"]).lower() in ["yes", "anytime touchdown"]]

                props_list.append({
                    "player": player,
                    "market": market,
                    "matchup": matchup,
                    "best_over": max(overs, key=lambda x: x["price"]) if overs else None,
                    "best_under": max(unders, key=lambda x: x["price"]) if unders else None,
                    "best_yes": max(yes_tds, key=lambda x: x["price"]) if yes_tds else None,
                    "discrepancy": disc_note,
                    "all_lines": lines_by_book
                })

        output = {
            "updated_at": datetime.now().strftime("%Y-%m-%d %I:%M:%S %p ET"),
            "sports_count": len(set(m["sport_label"] for m in matchups_list)),
            "matchups_count": len(matchups_list),
            "arbs_count": len(arbs_list),
            "props_count": len(props_list),
            "matchups": matchups_list,
            "arbs": arbs_list,
            "props": props_list
        }
        with open("mobile_data.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)
        print(f"Exported mobile_data.json ({len(matchups_list)} matchups, {len(arbs_list)} arbs, {len(props_list)} props).")
    except Exception as e:
        print(f"Warning: Could not export mobile_data.json: {e}")

def main():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Connecting to Google Sheets...")
    sheet = get_google_sheet()
    
    settings_sheet = sheet.worksheet("Settings")
    data_sheet = sheet.worksheet("Odds Data")
    depth_sheet = sheet.worksheet("Novig Market Depth")
    
    ensure_settings_rows(settings_sheet)
    
    print("Reading settings configuration...")
    settings = read_settings(settings_sheet)
    
    api_key = settings.get("The Odds API Key", "").strip()
    odds_format = settings.get("Odds Format (american or decimal)", "american").strip()
    fetch_props = settings.get("Fetch Player Props", True)
    props_horizon = float(settings.get("Props Time Horizon (Hours)", 36))
    
    if not api_key:
        print("Error: The Odds API Key is missing in sheet cell B2.")
        update_status(settings_sheet, "Error: Missing The Odds API Key.")
        sys.exit(1)
        
    # Get active sports from checkbox toggles
    sports = []
    sport_keys = [
        "NFL (americanfootball_nfl)", "NCAAF (americanfootball_ncaaf)",
        "NBA (basketball_nba)", "NCAAB (basketball_ncaab)",
        "WNBA (basketball_wnba)", "NCAAW Basketball (basketball_wncaab)",
        "MLB (baseball_mlb)", "NHL (icehockey_nhl)"
    ]
    for key in sport_keys:
        if settings.get(key) is True:
            sport_code = key.split("(")[1].split(")")[0]
            sports.append(sport_code)
            
    # Include tennis dynamically
    if settings.get("Tennis (all active tournaments)") is True:
        print("Scanning active tennis tournament keys...")
        active_tennis = get_active_tennis_sports(api_key)
        sports.extend(active_tennis)
        
    # Get bookmakers
    bookmakers = []
    books_keys = [
        ("Include Novig (Exchange)", "novig"),
        ("Include DraftKings", "draftkings"),
        ("Include FanDuel", "fanduel"),
        ("Include BetMGM", "betmgm"),
        ("Include Caesars (Requires Paid API Tier)", "williamhill_us"),
        ("Include Fanatics (Requires Paid API Tier)", "fanatics"),
        ("Include BetRivers", "betrivers")
    ]
    for key, code in books_keys:
        if settings.get(key) is True:
            bookmakers.append(code)
            
    if not sports:
        update_status(settings_sheet, "Error: No sports selected.")
        print("Error: No sports checked.")
        sys.exit(1)
        
    if not bookmakers:
        update_status(settings_sheet, "Error: No bookmakers selected.")
        print("Error: No bookmakers checked.")
        sys.exit(1)
        
    # 1. Fetch standard odds
    update_status(settings_sheet, "Refreshing standard odds...")
    odds_data, events_by_sport = fetch_odds_api(api_key, sports, bookmakers, odds_format)
    
    # 2. Fetch Novig GQL Depth if enabled
    depth_data = []
    if "novig" in bookmakers:
        update_status(settings_sheet, "Refreshing Novig order book depth...")
        
        # Translate checked sports to Novig leagues
        novig_leagues = []
        for sport in sports:
            mapped = map_sport_to_novig_league(sport)
            novig_leagues.extend(mapped)
        novig_leagues = list(set(novig_leagues)) # Deduplicate
        
        if novig_leagues:
            depth_data = fetch_novig_depth(novig_leagues, odds_format)
            
        if depth_data:
            print(f"Writing {len(depth_data)} rows of depth levels to 'Novig Market Depth' tab...")
            print("Clearing 'Novig Market Depth' tab...")
            depth_sheet.clear()
            depth_headers = [
                "Event Name", "Sport", "Market Type", "Outcome Name", "Line",
                "Side", "Odds", "Max Bet Size (Liquidity)", "Depth Level", "Outcome Class"
            ]
            depth_sheet.update(range_name="A1", values=[depth_headers] + depth_data)
        else:
            print("Warning: No Novig depth data retrieved. Preserving existing 'Novig Market Depth' tab.")
            
    # Match and embed Novig liquidity directly into the standard Odds Data rows,
    # and synthesize missing Novig rows directly from Novig GQL depth if The Odds API omitted them.
    odds_data_with_liquidity = []
    novig_existing = set()
    
    for row in odds_data:
        bookmaker = row[5]
        liquidity = ""
        
        if bookmaker.lower() == "novig":
            home_team = row[3]
            away_team = row[4]
            market_key = row[6]
            outcome_name = row[7]
            point = row[8]
            
            n_odds, liquidity = find_novig_quote(home_team, away_team, market_key, outcome_name, point, depth_data)
            # If Novig GQL has real-time odds, ensure the price reflects live exchange book
            if n_odds:
                row[9] = n_odds
            novig_existing.add((row[0], row[6], row[7], str(row[8])))
            
        row_copy = list(row)
        row_copy.append(liquidity)
        odds_data_with_liquidity.append(row_copy)
        
    # Synthesize missing Novig rows if Novig was selected
    if "novig" in bookmakers and depth_data:
        update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Collect distinct market outcomes across all other bookmakers
        outcomes_by_game = {}
        for row in odds_data:
            eid, sport_title, formatted_commence, home_team, away_team, book_title, market_key, name, point, price, formatted_update = row
            key = (eid, market_key, name, str(point))
            if key not in novig_existing and key not in outcomes_by_game:
                outcomes_by_game[key] = (eid, sport_title, formatted_commence, home_team, away_team, market_key, name, point)
                
        synthesized_count = 0
        for key, meta in outcomes_by_game.items():
            eid, sport_title, formatted_commence, home_team, away_team, market_key, name, point = meta
            n_odds, n_liq = find_novig_quote(home_team, away_team, market_key, name, point, depth_data)
            if n_odds is not None:
                synthesized_row = [
                    eid, sport_title, formatted_commence, home_team, away_team,
                    "Novig", market_key, name, point, n_odds, update_time, n_liq
                ]
                odds_data_with_liquidity.append(synthesized_row)
                synthesized_count += 1
                
        print(f"Synthesized {synthesized_count} missing Novig rows directly from Novig GraphQL depth.")
        
    # Write to Odds Data sheet
    print(f"Writing {len(odds_data_with_liquidity)} rows of odds with matched liquidity to 'Odds Data' tab...")
    data_sheet.clear_basic_filter()
    
    print("Clearing 'Odds Data' tab...")
    data_sheet.clear()
    
    headers = [
        "Event ID", "Sport", "Commence Time (ET)", "Home Team", "Away Team",
        "Bookmaker", "Market", "Outcome", "Point", "Price", "Last Update (ET)",
        "Liquidity (USD)"
    ]
    
    if odds_data_with_liquidity:
        total_odds_rows = len(odds_data_with_liquidity) + 1
        if data_sheet.row_count < total_odds_rows:
            print(f"Expanding 'Odds Data' sheet from {data_sheet.row_count} to {total_odds_rows + 200} rows...")
            data_sheet.resize(rows=total_odds_rows + 200, cols=max(15, data_sheet.col_count))
        data_sheet.update(range_name="A1", values=[headers] + odds_data_with_liquidity)
    else:
        data_sheet.update(range_name="A1", values=[headers])
        
    # 3. Fetch Player Props if enabled
    props_data = []
    if fetch_props:
        # Determine allowed sports for player props
        allowed_prop_sports = []
        for label, sport_code, _ in PROPS_SPORT_CONFIG:
            if settings.get(label) is True:
                allowed_prop_sports.append(sport_code)
                
        # If no specific prop sport toggles are checked, fallback to active checked sports
        if not allowed_prop_sports:
            allowed_prop_sports = [s for s in sports if s in PROP_MARKETS]
            
        print(f"Player props active sports: {allowed_prop_sports}")
        update_status(settings_sheet, "Refreshing player props...")
        props_data = fetch_player_props(api_key, events_by_sport, bookmakers, odds_format, props_horizon, allowed_prop_sports)
        
        # Connect to or create 'Player Props Data' tab
        try:
            props_sheet = sheet.worksheet("Player Props Data")
        except gspread.exceptions.WorksheetNotFound:
            print("Creating 'Player Props Data' worksheet...")
            props_sheet = sheet.add_worksheet(title="Player Props Data", rows=max(5000, len(props_data) + 500), cols=15)
            
        print(f"Writing {len(props_data)} rows of player props to 'Player Props Data' tab...")
        props_sheet.clear_basic_filter()
        props_sheet.clear()
        
        props_headers = [
            "Event ID", "Sport", "Commence Time (ET)", "Matchup",
            "Player Name", "Prop Market", "Outcome", "Line",
            "Bookmaker", "Price", "Last Update (ET)"
        ]
        
        if props_data:
            all_props = [props_headers] + props_data
            if props_sheet.row_count < len(all_props):
                print(f"Expanding 'Player Props Data' sheet from {props_sheet.row_count} to {len(all_props) + 500} rows...")
                props_sheet.resize(rows=len(all_props) + 500, cols=max(15, props_sheet.col_count))
            chunk_size = 2000
            for i in range(0, len(all_props), chunk_size):
                chunk = all_props[i:i + chunk_size]
                props_sheet.update(range_name=f"A{i + 1}", values=chunk)
        else:
            props_sheet.update(range_name="A1", values=[props_headers])
            
    status_summary = f"Odds refresh complete. Updated {len(odds_data)} game lines"
    if fetch_props:
        status_summary += f" & {len(props_data)} player props."
    else:
        status_summary += "."
    update_status(settings_sheet, status_summary)
    
    # Export mobile-ready JSON bundle for mobile web app
    export_mobile_data(odds_data_with_liquidity, props_data)
    
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Done!")

if __name__ == "__main__":
    main()
