import json
import os
from datetime import datetime, timedelta
from utils.session_store import get_transactions

# ── Thresholds ──
VELOCITY_RULES = [
    {"window_seconds": 60,  "max_txns": 3,     "severity": "SUSPICIOUS", "reason": "3 transactions in 60 seconds"},
    {"window_seconds": 300, "max_txns": 5,      "severity": "FRAUD",      "reason": "5 transactions in 5 minutes"},
    {"window_seconds": 60,  "max_amount": 10000,"severity": "SUSPICIOUS", "reason": "₹10,000+ spent in 60 seconds"},
    {"window_seconds": 300, "max_amount": 25000,"severity": "FRAUD",      "reason": "₹25,000+ spent in 5 minutes"},
]



def check_velocity(user_id: str, current_amount: float, txn_log: list = None) -> dict:
    """
    Check if a user's recent transaction velocity is suspicious.
    Uses real time-window based detection.
    Accepts optional in-memory txn_log from API for real-time accuracy.
    """
    if txn_log is not None:
        user_txns = txn_log
    else:
        all_txns  = get_transactions()
        user_txns = [
            t for t in all_txns
            if t.get("user") == user_id and t.get("result") != "BLOCKED"
        ]

    

    # ── REAL MODE: time-window based (for production accuracy) ──
    now             = datetime.now()
    triggered_rules = []
    best_recent     = []

    for rule in VELOCITY_RULES:
        window_start  = now - timedelta(seconds=rule["window_seconds"])
        window_recent = []

        for t in user_txns:
            try:
                ts = datetime.strptime(t["timestamp"], "%Y-%m-%d %H:%M:%S")
                if ts >= window_start:
                    window_recent.append(t)
            except:
                continue

        rule_triggered = False

        if "max_txns" in rule and len(window_recent) >= rule["max_txns"]:
            triggered_rules.append(rule)
            rule_triggered = True

        if "max_amount" in rule:
            total = sum(t.get("amount", 0) for t in window_recent) + current_amount
            if total >= rule["max_amount"]:
                triggered_rules.append(rule)
                rule_triggered = True

        if rule_triggered and len(window_recent) > len(best_recent):
            best_recent = window_recent

    if not triggered_rules:
        return {"triggered": False, "severity": "SAFE",
                "reason": "", "velocity_score": 0, "recent_count": 0}

    severity = "SAFE"
    reasons  = []
    for rule in triggered_rules:
        reasons.append(rule["reason"])
        if rule["severity"] == "FRAUD":
            severity = "FRAUD"
        elif rule["severity"] == "SUSPICIOUS" and severity != "FRAUD":
            severity = "SUSPICIOUS"

    velocity_score = min(len(triggered_rules) * 25, 100)
    if severity == "FRAUD":
        velocity_score = max(velocity_score, 75)

    return {
        "triggered"      : True,
        "severity"       : severity,
        "reason"         : " · ".join(reasons),
        "velocity_score" : velocity_score,
        "recent_count"   : len(best_recent)
    }


def get_user_velocity_stats(user_id: str) -> dict:
    """Get full velocity stats for a user — used by security dashboard."""
    all_txns  = get_transactions()
    user_txns = [t for t in all_txns if t.get("user") == user_id]
    now       = datetime.now()

    def count_in_window(seconds):
        start = now - timedelta(seconds=seconds)
        return sum(
            1 for t in user_txns
            if _parse_ts(t.get("timestamp", "")) >= start
        )

    def amount_in_window(seconds):
        start = now - timedelta(seconds=seconds)
        return sum(
            t.get("amount", 0) for t in user_txns
            if _parse_ts(t.get("timestamp", "")) >= start
            and t.get("result", "") != "BLOCKED"
        )

    return {
        "user_id"          : user_id,
        "total_txns"       : len(user_txns),
        "txns_1min"        : count_in_window(60),
        "txns_5min"        : count_in_window(300),
        "txns_1hr"         : count_in_window(3600),
        "amount_1min"      : amount_in_window(60),
        "amount_5min"      : amount_in_window(300),
        "amount_1hr"       : amount_in_window(3600),
        "is_high_velocity" : count_in_window(60) >= 3 or count_in_window(300) >= 5
    }


def _parse_ts(ts_str):
    try:
        return datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
    except:
        return datetime.min