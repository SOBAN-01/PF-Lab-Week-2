"""
ShieldAI - Backend / Business Logic Layer
===========================================
All authentication, user management, history management, profile
management, and JSON file handling lives here. No GUI code. No Flask.
No HTTP. Every function returns a plain Python dict so it can be called
identically from main.py (tkinter GUI) or from this file's own CLI mode.

Data files (created automatically on first run, next to this script /
the packaged executable):
    users.json    - {username: {password_hash, profile_image, created_scans}}
    history.json  - {username: [scan_record, ...]}

Folders:
    profiles/  - uploaded profile images
    assets/    - static GUI assets (icons, etc.)
"""

import os
import sys
import json
import uuid
import shutil
import hashlib
import getpass
import logging
from datetime import datetime

from scanner import analyze_url


# ── Paths (work both as a plain script and as a PyInstaller --onefile exe) ──

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

USERS_FILE = os.path.join(BASE_DIR, "users.json")
HISTORY_FILE = os.path.join(BASE_DIR, "history.json")
PROFILES_DIR = os.path.join(BASE_DIR, "profiles")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

MIN_PASSWORD_LENGTH = 6

# Tkinter's built-in PhotoImage (no Pillow dependency) only reliably reads
# these formats, so profile images are restricted to them. This keeps
# PyInstaller packaging dependency-free as required.
ALLOWED_IMAGE_EXTENSIONS = {".png", ".gif", ".ppm", ".pgm"}

logging.basicConfig(
    filename=os.path.join(BASE_DIR, "shieldai.log"),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def ensure_directories():
    os.makedirs(PROFILES_DIR, exist_ok=True)
    os.makedirs(ASSETS_DIR, exist_ok=True)


# ---------------- JSON FILE HELPERS ----------------

def load_json(filename, default):
    """Load a JSON file, transparently creating or repairing it if needed."""
    if not os.path.exists(filename):
        save_json(filename, default)
        return default

    try:
        with open(filename, "r") as file:
            return json.load(file)
    except json.JSONDecodeError:
        logging.error(f"Corrupted JSON file repaired: {filename}")
        save_json(filename, default)
        return default


def save_json(filename, data):
    """Atomic write: write to a temp file then replace, to avoid corruption."""
    try:
        temp = filename + ".tmp"
        with open(temp, "w") as file:
            json.dump(data, file, indent=4)
        os.replace(temp, filename)
        return True
    except Exception as e:
        logging.error(f"File saving error {filename}: {e}")
        return False


# ---------------- PASSWORD HELPERS ----------------

def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(password, password_hash):
    return hash_password(password) == password_hash


# ---------------- VALIDATION HELPERS ----------------

def _validate_username(username):
    if not username or not username.strip():
        return "Username is required"
    if len(username.strip()) < 3:
        return "Username must be at least 3 characters"
    return None


def _validate_password(password):
    if not password:
        return "Password is required"
    if len(password) < MIN_PASSWORD_LENGTH:
        return f"Password must contain a minimum of {MIN_PASSWORD_LENGTH} characters"
    return None


# ---------------- AUTHENTICATION ----------------

def signup(username, password):
    """Create a new account. Returns {"success": bool, "message"/"error": str}."""
    username = (username or "").strip()

    err = _validate_username(username)
    if err:
        return {"success": False, "error": err}

    err = _validate_password(password)
    if err:
        return {"success": False, "error": err}

    users = load_json(USERS_FILE, {})

    if username in users:
        return {"success": False, "error": "Username already exists"}

    users[username] = {
        "password_hash": hash_password(password),
        "profile_image": None,
        "created_scans": 0,
    }

    save_json(USERS_FILE, users)
    logging.info(f"New user created: {username}")

    return {"success": True, "message": "Account created successfully"}


def login(username, password):
    """Validate credentials. Returns {"success": bool, "username"/"error": str}."""
    username = (username or "").strip()
    users = load_json(USERS_FILE, {})

    user = users.get(username)
    if not user or not verify_password(password or "", user["password_hash"]):
        logging.warning(f"Failed login attempt: {username}")
        return {"success": False, "error": "Invalid username or password"}

    logging.info(f"User logged in: {username}")
    return {"success": True, "username": username, "message": "Login successful"}


# ---------------- PROFILE MANAGEMENT ----------------

def get_profile(username):
    """Return profile info + basic stats for a user."""
    users = load_json(USERS_FILE, {})
    user = users.get(username)
    if not user:
        return {"success": False, "error": "User not found"}

    history = load_json(HISTORY_FILE, {}).get(username, [])
    threats = sum(1 for s in history if s.get("danger_level") == "DANGER")

    return {
        "success": True,
        "username": username,
        "profile_image": user.get("profile_image"),
        "total_scans": len(history),
        "threats_detected": threats,
    }


def update_profile(username, new_username):
    """Rename a user, preserving their profile image and full scan history."""
    new_username = (new_username or "").strip()

    err = _validate_username(new_username)
    if err:
        return {"success": False, "error": err}

    users = load_json(USERS_FILE, {})

    if username not in users:
        return {"success": False, "error": "User not found"}

    if new_username == username:
        return {"success": True, "message": "Username unchanged", "username": username}

    if new_username in users:
        return {"success": False, "error": "That username is already taken"}

    users[new_username] = users.pop(username)
    save_json(USERS_FILE, users)

    # Re-key history so existing scan records move with the renamed account
    history = load_json(HISTORY_FILE, {})
    if username in history:
        history[new_username] = history.pop(username)
        for record in history[new_username]:
            record["username"] = new_username
        save_json(HISTORY_FILE, history)

    logging.info(f"Username changed: {username} -> {new_username}")
    return {"success": True, "message": "Username updated", "username": new_username}


def set_profile_image(username, image_path):
    """Copy an image into profiles/ and link it to the user's account."""
    users = load_json(USERS_FILE, {})
    if username not in users:
        return {"success": False, "error": "User not found"}

    if not image_path or not os.path.exists(image_path):
        return {"success": False, "error": "Image file not found"}

    ext = os.path.splitext(image_path)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        return {
            "success": False,
            "error": "Unsupported image format. Please use PNG or GIF",
        }

    ensure_directories()
    new_filename = f"{username}_{uuid.uuid4().hex[:8]}{ext}"
    destination = os.path.join(PROFILES_DIR, new_filename)

    try:
        shutil.copyfile(image_path, destination)
    except Exception as e:
        logging.error(f"Profile image copy failed for {username}: {e}")
        return {"success": False, "error": "Could not save image"}

    users[username]["profile_image"] = os.path.join("profiles", new_filename)
    save_json(USERS_FILE, users)

    logging.info(f"Profile image updated: {username}")
    return {"success": True, "message": "Profile image updated", "profile_image": users[username]["profile_image"]}


# ---------------- SCANNING ----------------

def scan_url(username, url):
    """Run the phishing analysis engine and persist the result to history."""
    users = load_json(USERS_FILE, {})
    if username not in users:
        return {"success": False, "error": "User not found"}

    if not url or not url.strip():
        return {"success": False, "error": "URL is required"}

    result = analyze_url(url.strip())

    record = {
        "scan_id": uuid.uuid4().hex,
        "username": username,
        "url": result["url"],
        "risk_score": result["risk_score"],
        "danger_level": result["danger_level"],
        "reasons": result["reasons"],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    history = load_json(HISTORY_FILE, {})
    history.setdefault(username, [])
    history[username].append(record)
    save_json(HISTORY_FILE, history)

    users[username]["created_scans"] = users[username].get("created_scans", 0) + 1
    save_json(USERS_FILE, users)

    logging.info(f"Scan performed by {username}: {record['url']} -> {record['danger_level']}")

    record["success"] = True
    return record


# ---------------- HISTORY MANAGEMENT ----------------

def get_history(username):
    """Return a user's scan history, newest first."""
    history = load_json(HISTORY_FILE, {})
    records = history.get(username, [])
    return sorted(records, key=lambda r: r.get("timestamp", ""), reverse=True)


def search_history(username, query):
    """Search a user's history by URL substring, danger level, or date."""
    records = get_history(username)
    if not query or not query.strip():
        return records

    query = query.strip().lower()
    return [
        r for r in records
        if query in str(r.get("url", "")).lower()
        or query in str(r.get("danger_level", "")).lower()
        or query in str(r.get("timestamp", "")).lower()
    ]


def sort_history(username, method):
    """
    Sort a user's history.
    method: "newest" | "oldest" | "highest" | "lowest"
    """
    records = get_history(username)  # already newest-first

    if method == "oldest":
        return list(reversed(records))
    if method == "highest":
        return sorted(records, key=lambda r: r.get("risk_score", 0), reverse=True)
    if method == "lowest":
        return sorted(records, key=lambda r: r.get("risk_score", 0))
    return records  # "newest" (default)


def delete_scan(username, scan_id):
    """Delete a single scan record by its scan_id."""
    history = load_json(HISTORY_FILE, {})
    records = history.get(username, [])

    new_records = [r for r in records if r.get("scan_id") != scan_id]
    if len(new_records) == len(records):
        return {"success": False, "error": "Scan not found"}

    history[username] = new_records
    save_json(HISTORY_FILE, history)

    logging.info(f"Scan deleted by {username}: {scan_id}")
    return {"success": True, "message": "Scan deleted"}


# ══════════════════════════════════════════════════════════════════════════
#  CLI MODE
#  Uses the exact same backend functions as the GUI - no duplicated logic.
# ══════════════════════════════════════════════════════════════════════════

def _cli_pause():
    input("\nPress Enter to continue...")


def _cli_print_result(record):
    print(f"\nURL          : {record.get('url')}")
    print(f"Risk Score   : {record.get('risk_score')}/100")
    print(f"Danger Level : {record.get('danger_level')}")
    print("Reasons      :")
    for reason in record.get("reasons", []):
        print(f"   - {reason}")


def _cli_print_history(records):
    if not records:
        print("\nNo scan history found.")
        return
    print(f"\n{'STATUS':<12}{'SCORE':<8}{'TIMESTAMP':<22}URL")
    print("-" * 80)
    for r in records:
        print(f"{r.get('danger_level',''):<12}{r.get('risk_score',0):<8}"
              f"{r.get('timestamp',''):<22}{r.get('url','')}")


def _cli_signup():
    print("\n--- Create Account ---")
    username = input("Choose a username: ").strip()
    password = getpass.getpass("Choose a password: ")
    result = signup(username, password)
    print(result.get("message") or result.get("error"))


def _cli_login():
    print("\n--- Login ---")
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ")
    result = login(username, password)
    if result["success"]:
        print(result["message"])
        return result["username"]
    print(result["error"])
    return None


def _cli_scan(username):
    url = input("\nEnter a URL to scan: ").strip()
    result = scan_url(username, url)
    if result.get("success"):
        _cli_print_result(result)
    else:
        print(result.get("error"))


def _cli_history(username):
    _cli_print_history(get_history(username))


def _cli_search(username):
    query = input("\nSearch by URL / danger level / date: ").strip()
    _cli_print_history(search_history(username, query))


def _cli_sort(username):
    print("\nSort by: 1) Newest  2) Oldest  3) Highest score  4) Lowest score")
    choice = input("Choice: ").strip()
    method = {"1": "newest", "2": "oldest", "3": "highest", "4": "lowest"}.get(choice, "newest")
    _cli_print_history(sort_history(username, method))


def _cli_delete(username):
    scan_id = input("\nEnter the scan_id to delete: ").strip()
    result = delete_scan(username, scan_id)
    print(result.get("message") or result.get("error"))


def _cli_profile(username):
    print("\n--- Profile ---")
    print("1) View profile")
    print("2) Change username")
    print("3) Change profile image")
    choice = input("Choice: ").strip()

    if choice == "1":
        profile = get_profile(username)
        print(f"\nUsername          : {profile.get('username')}")
        print(f"Profile image      : {profile.get('profile_image') or '(none)'}")
        print(f"Total scans        : {profile.get('total_scans')}")
        print(f"Threats detected   : {profile.get('threats_detected')}")
        return username

    if choice == "2":
        new_username = input("New username: ").strip()
        result = update_profile(username, new_username)
        print(result.get("message") or result.get("error"))
        if result.get("success"):
            return result.get("username", username)
        return username

    if choice == "3":
        path = input("Path to PNG/GIF image file: ").strip()
        result = set_profile_image(username, path)
        print(result.get("message") or result.get("error"))
        return username

    return username


def run_cli():
    ensure_directories()
    print("=" * 50)
    print("   ShieldAI - Phishing Link Detector (CLI)")
    print("=" * 50)

    current_user = None

    while True:
        if not current_user:
            print("\n1) Login\n2) Signup\n3) Exit")
            choice = input("Choice: ").strip()
            if choice == "1":
                current_user = _cli_login()
            elif choice == "2":
                _cli_signup()
            elif choice == "3":
                break
            else:
                print("Invalid choice.")
            continue

        print(f"\nLogged in as: {current_user}")
        print("1) Scan URL\n2) View History\n3) Search History\n4) Sort History"
              "\n5) Delete Scan\n6) Profile\n7) Logout\n8) Exit")
        choice = input("Choice: ").strip()

        if choice == "1":
            _cli_scan(current_user)
        elif choice == "2":
            _cli_history(current_user)
        elif choice == "3":
            _cli_search(current_user)
        elif choice == "4":
            _cli_sort(current_user)
        elif choice == "5":
            _cli_delete(current_user)
        elif choice == "6":
            current_user = _cli_profile(current_user)
        elif choice == "7":
            current_user = None
        elif choice == "8":
            break
        else:
            print("Invalid choice.")

    print("\nGoodbye.")


if __name__ == "__main__":
    run_cli()
