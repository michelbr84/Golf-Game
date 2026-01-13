import json
import os

PROFILE_FILE = "profiles.json"

current_user = None
profile_data = {}

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

def get_coins():
    if current_user and current_user in profile_data:
        return profile_data[current_user]["coins"]
    return 0

def add_coins(amount):
    if current_user and current_user in profile_data:
        profile_data[current_user]["coins"] += amount
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

def is_ball_unlocked(color_str):
    if current_user and current_user in profile_data:
        return color_str in profile_data[current_user]["unlocked_balls"]
    return False

def unlock_ball(color_str):
    if current_user and current_user in profile_data:
        if color_str not in profile_data[current_user]["unlocked_balls"]:
            profile_data[current_user]["unlocked_balls"].append(color_str)
            save_data()
