import json
import os
from datetime import datetime
from utils.session_store import get_transactions

_HERE           = os.path.dirname(os.path.abspath(__file__))
REPUTATION_FILE = os.path.join(_HERE, "merchant_reputation.json")

def _load_reputation():
    if not os.path.exists(REPUTATION_FILE):
        return {"blacklist": [], "whitelist": [], "merchant_stats": {}}
    with open(REPUTATION_FILE, "r") as f:
        return json.load(f)

def _save_reputation(data):
    os.makedirs(os.path.dirname(REPUTATION_FILE), exist_ok=True)
    with open(REPUTATION_FILE, "w") as f:
        json.dump(data, f, indent=2)

def update_merchant_stats(merchant: str, status: str, amount: float, user: str = "unknown"):
    """Called after every transaction to update merchant reputation."""
    data  = _load_reputation()
    stats = data["merchant_stats"]
    key   = merchant.lower().strip()

    if key not in stats:
        stats[key] = {
            "merchant"     : merchant,
            "total_txns"   : 0,
            "fraud_count"  : 0,
            "suspicious_count": 0,
            "safe_count"   : 0,
            "total_amount" : 0,
            "first_seen"   : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "last_seen"    : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    stats[key]["total_txns"]   += 1
    stats[key]["total_amount"] += amount
    stats[key]["last_seen"]     = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if status == "FRAUD":
        stats[key]["fraud_count"] += 1
    elif status == "SUSPICIOUS":
        stats[key]["suspicious_count"] += 1
    else:
        stats[key]["safe_count"] += 1

    # ── Fraud Pattern Memory ──
    # Rule 1: fraud rate > 50% with 3+ transactions
    if stats[key]["total_txns"] >= 3:
        fraud_rate = stats[key]["fraud_count"] / stats[key]["total_txns"]
        if fraud_rate > 0.5 and key not in data["blacklist"]:
            data["blacklist"].append(key)
            data.setdefault("blacklist_reasons", {})[key] = \
                f"Auto-blacklisted: fraud rate {fraud_rate:.0%} over {stats[key]['total_txns']} transactions"

    # Rule 2: flagged by 3+ different users
    if "user_flags" not in stats[key]:
        stats[key]["user_flags"] = []
    if txn_user := next((t.get("user") for t in get_transactions()
                         if t.get("merchant","").lower().strip() == key
                         and t.get("status") == "FRAUD"), None):
        if txn_user and txn_user not in stats[key]["user_flags"]:
            stats[key]["user_flags"].append(txn_user)

    if len(stats[key].get("user_flags", [])) >= 3 and key not in data["blacklist"]:
        data["blacklist"].append(key)
        data.setdefault("blacklist_reasons", {})[key] = \
            f"Auto-blacklisted: flagged by {len(stats[key]['user_flags'])} different users"

    data["merchant_stats"] = stats
    _save_reputation(data)

def check_merchant_reputation(merchant: str) -> dict:
    """
    Returns reputation score for a merchant.
    {
        "score": 0-100 (higher = more suspicious),
        "reason": str,
        "is_blacklisted": bool,
        "is_new": bool,
        "fraud_rate": float
    }
    """
    data  = _load_reputation()
    key   = merchant.lower().strip()

    # Check blacklist
    if key in data["blacklist"]:
        return {
            "score"         : 85,
            "reason"        : f"Merchant '{merchant}' is blacklisted",
            "is_blacklisted": True,
            "is_new"        : False,
            "fraud_rate"    : 1.0
        }

    # Check whitelist
    if key in data["whitelist"]:
        return {
            "score"         : 0,
            "reason"        : "",
            "is_blacklisted": False,
            "is_new"        : False,
            "fraud_rate"    : 0.0
        }

    stats = data["merchant_stats"].get(key)

    # Brand new merchant
    if not stats:
        return {
            "score"         : 15,
            "reason"        : f"First transaction with '{merchant}'",
            "is_blacklisted": False,
            "is_new"        : True,
            "fraud_rate"    : 0.0
        }

    total = stats["total_txns"]
    fraud_rate = stats["fraud_count"] / total if total > 0 else 0
    susp_rate  = stats["suspicious_count"] / total if total > 0 else 0

    score  = 0
    reason = []

    if fraud_rate > 0.3:
        score  += 60
        reason.append(f"High fraud rate ({fraud_rate:.0%})")
    elif fraud_rate > 0.1:
        score  += 30
        reason.append(f"Elevated fraud rate ({fraud_rate:.0%})")

    if susp_rate > 0.4:
        score  += 20
        reason.append(f"Frequently suspicious ({susp_rate:.0%})")

    return {
        "score"         : min(score, 100),
        "reason"        : " · ".join(reason) if reason else "",
        "is_blacklisted": False,
        "is_new"        : False,
        "fraud_rate"    : fraud_rate
    }

def blacklist_merchant(merchant: str):
    data = _load_reputation()
    key  = merchant.lower().strip()
    if key not in data["blacklist"]:
        data["blacklist"].append(key)
    _save_reputation(data)
    return True

def whitelist_merchant(merchant: str):
    data = _load_reputation()
    key  = merchant.lower().strip()
    if key not in data["whitelist"]:
        data["whitelist"].append(key)
    if key in data["blacklist"]:
        data["blacklist"].remove(key)
    _save_reputation(data)
    return True

def get_all_merchant_stats():
    data = _load_reputation()
    return {
        "blacklist"     : data["blacklist"],
        "whitelist"     : data["whitelist"],
        "merchant_stats": data["merchant_stats"]
    }