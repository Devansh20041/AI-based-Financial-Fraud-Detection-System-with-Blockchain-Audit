import json
import os
from datetime import datetime

_HERE      = os.path.dirname(os.path.abspath(__file__))
STORE_PATH = os.path.join(_HERE, "session_data.json")

def _load():
    if not os.path.exists(STORE_PATH):
        return {"transactions": [], "alerts": [], "users": {}}
    with open(STORE_PATH, "r") as f:
        return json.load(f)

def _save(data):
    os.makedirs(os.path.dirname(STORE_PATH), exist_ok=True)
    with open(STORE_PATH, "w") as f:
        json.dump(data, f, indent=2)

def add_transaction(txn: dict):
    data = _load()
    data["transactions"].insert(0, txn)
    data["transactions"] = data["transactions"][:500]  # keep last 500 for velocity accuracy
    _save(data)

def get_transactions():
    return _load().get("transactions", [])

def add_alert(alert: dict):
    data = _load()
    data["alerts"].insert(0, alert)
    data["alerts"] = data["alerts"][:50]
    _save(data)

def get_alerts():
    return _load().get("alerts", [])

def register_user(username, password_hash, full_name, account_no):
    data = _load()
    if username in data["users"]:
        return False
    data["users"][username] = {
        "username"    : username,
        "password"    : password_hash,
        "full_name"   : full_name,
        "account_no"  : account_no,
        "balance"     : 50000.00,
        "created_at"  : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    _save(data)
    return True

def get_user(username):
    return _load()["users"].get(username)

def update_balance(username, amount):
    data = _load()
    if username in data["users"]:
        data["users"][username]["balance"] -= amount
        _save(data)

def clear_alerts():
    data = _load()
    data["alerts"] = []
    _save(data)