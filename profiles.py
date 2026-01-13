import json
import os

PROFILE_FILE = "profiles.json"

current_user = None
profile_data = {}

DEFAULT_BALLS = [
    "255,255,255", # White (Unlocked by default)
    "255,0,0",
    "0,255,0",
    "0,0,255",
    "255,255,0",
    "255,0,255",
    "0,255,255",
    "192,192,192",
    "128,128,128",
    "128,0,0",
    "128,128,0",
    "0,128,0",
    "128,0,128",
    "0,128,128",
    "0,0,128",
    "255,165,0"
]

def load_data():
    global profile_data
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, 'r') as f:
                profile_data = json.load(f)
        except:
            profile_data = {}
    else:
        profile_data = {}

def save_data():
    global profile_data
    try:
        with open(PROFILE_FILE, 'w') as f:
            json.dump(profile_data, f, indent=4)
    except Exception as e:
        print(f"Error saving profiles: {e}")

def login(username):
    global current_user, profile_data
    load_data()
    current_user = username
    if current_user not in profile_data:
        profile_data[current_user] = {
            "coins": 0,
            "best_score": 999,
            "unlocked_balls": ["255,255,255"] # White default
        }
        save_data()
    # Ensure all fields exist (migration)
    if "coins" not in profile_data[current_user]: profile_data[current_user]["coins"] = 0
    if "best_score" not in profile_data[current_user]: profile_data[current_user]["best_score"] = 999
    if "unlocked_balls" not in profile_data[current_user]: profile_data[current_user]["unlocked_balls"] = ["255,255,255"]
    if "equipped_ball" not in profile_data[current_user]: profile_data[current_user]["equipped_ball"] = "255,255,255"

def logout():
    global current_user
    current_user = None

def get_coins():
    if current_user and current_user in profile_data:
        return profile_data[current_user]["coins"]
    return 0

def add_coins(amount):
    if current_user and current_user in profile_data:
        profile_data[current_user]["coins"] += amount
        save_data()

def set_coins(amount):
    if current_user and current_user in profile_data:
        profile_data[current_user]["coins"] = amount
        save_data()

def get_best_score():
    if current_user and current_user in profile_data:
        return profile_data[current_user]["best_score"]
    return 999

def update_best_score(score):
    if current_user and current_user in profile_data:
        if score < profile_data[current_user]["best_score"]:
            profile_data[current_user]["best_score"] = score
            save_data()
            return True
    return False

def unlock_ball(color_str):
    if current_user and current_user in profile_data:
        if color_str not in profile_data[current_user]["unlocked_balls"]:
            profile_data[current_user]["unlocked_balls"].append(color_str)
            save_data()

def is_ball_unlocked(color_str):
    if current_user and current_user in profile_data:
        return color_str in profile_data[current_user]["unlocked_balls"]
    return False

def equip_ball(color_str):
    if current_user and current_user in profile_data:
        if is_ball_unlocked(color_str):
            profile_data[current_user]["equipped_ball"] = color_str
            save_data()

def get_equipped_ball():
    if current_user and current_user in profile_data:
        val = profile_data[current_user].get("equipped_ball", "255,255,255")
        try:
             # Validate if it's a tuple-string
             if "," not in val: return "255,255,255"
             return val
        except:
             return "255,255,255"
    return "255,255,255"

def get_balls():
    """Returns list of dicts for UI: {color: str, locked: bool, equipped: bool}"""
    balls = []
    equipped = get_equipped_ball()
    
    for b in DEFAULT_BALLS:
        is_locked = not is_ball_unlocked(b)
        is_equipped = (b == equipped)
        # Force white unlock if bugged
        if b == "255,255,255": is_locked = False
        
        balls.append({
            "color": b,
            "locked": is_locked,
            "equipped": is_equipped
        })
    return balls
