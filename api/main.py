from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import numpy as np
import pickle
import json
import sys
import os
from datetime import datetime

# ── Add project root to path ──
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
from blockchain.blockchain import Blockchain
from utils.velocity_checker import check_velocity
from utils.merchant_reputation import check_merchant_reputation, update_merchant_stats

# ── Initialize App ──
app = FastAPI(
    title="VaultSense API",
    description="VaultSense — Secure Financial Monitoring System · Fraud Detection + Blockchain Verification",
    version="1.0.0"
)

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Load Models ──
print("📦 Loading models...")
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_HERE)

with open(os.path.join(_ROOT, 'models', 'isolation_forest.pkl'), 'rb') as f:
    iso_model = pickle.load(f)
with open(os.path.join(_ROOT, 'models', 'random_forest.pkl'), 'rb') as f:
    rf_model = pickle.load(f)
with open(os.path.join(_ROOT, 'models', 'xgboost.pkl'), 'rb') as f:
    xgb_model = pickle.load(f)
with open(os.path.join(_ROOT, 'models', 'best_model_name.pkl'), 'rb') as f:
    best_model_name = pickle.load(f)
with open(os.path.join(_ROOT, 'models', 'scaler.pkl'), 'rb') as f:
    scaler = pickle.load(f)
with open(os.path.join(_ROOT, 'models', 'feature_columns.pkl'), 'rb') as f:
    feature_columns = pickle.load(f)
with open(os.path.join(_ROOT, 'profiles', 'user_profiles.json'), 'r') as f:
    user_profiles = json.load(f)

# ── Pick best model ──
best_model = xgb_model if best_model_name == "XGBoost" else rf_model
print(f"🏆 Using: {best_model_name}")

print("✅ All models loaded!")

# ── Initialize Blockchain ──
blockchain = Blockchain(difficulty=2)
print("⛓ Blockchain initialized!")

# ── Transaction Counter ──
tx_counter = {"count": 1000}

# ── In-memory velocity log (resets on API restart) ──
from collections import defaultdict
velocity_log = defaultdict(list)

# ══════════════════════════════════════════
#              SCHEMAS
# ══════════════════════════════════════════

class TransactionInput(BaseModel):
    user_id: str
    amount: float
    merchant: str
    merchant_category: str
    hour: int  # 0-23
    # V1-V28 features (optional, defaults to 0)
    V1: Optional[float] = 0.0
    V2: Optional[float] = 0.0
    V3: Optional[float] = 0.0
    V4: Optional[float] = 0.0
    V5: Optional[float] = 0.0
    V6: Optional[float] = 0.0
    V7: Optional[float] = 0.0
    V8: Optional[float] = 0.0
    V9: Optional[float] = 0.0
    V10: Optional[float] = 0.0
    V11: Optional[float] = 0.0
    V12: Optional[float] = 0.0
    V13: Optional[float] = 0.0
    V14: Optional[float] = 0.0
    V15: Optional[float] = 0.0
    V16: Optional[float] = 0.0
    V17: Optional[float] = 0.0
    V18: Optional[float] = 0.0
    V19: Optional[float] = 0.0
    V20: Optional[float] = 0.0
    V21: Optional[float] = 0.0
    V22: Optional[float] = 0.0
    V23: Optional[float] = 0.0
    V24: Optional[float] = 0.0
    V25: Optional[float] = 0.0
    V26: Optional[float] = 0.0
    V27: Optional[float] = 0.0
    V28: Optional[float] = 0.0
    Time: Optional[float] = 0.0
    
    

# UserLogin schema reserved for future /login endpoint
# class UserLogin(BaseModel):
#     username: str
#     password: str

# ══════════════════════════════════════════
#              HELPERS
# ══════════════════════════════════════════

def compute_risk_score(transaction: TransactionInput):
    # Simulate V-features based on transaction context
    feature_dict = {col: 0.0 for col in feature_columns}

    # Inject suspicious V-feature patterns based on context
    is_suspicious_category = transaction.merchant_category in [
        "Wire Transfer", "Crypto Exchange", "ATM Withdrawal"
    ]
    is_odd_hour = transaction.hour < 5 or transaction.hour > 22
    is_high_amount = transaction.amount > 1000

    if is_suspicious_category and is_odd_hour:
        # Strong fraud signal
        feature_dict.update({
            "V1": -3.5, "V2": -2.8, "V3": -3.1,
            "V4":  3.2, "V9": -2.5, "V10": -3.8,
            "V11": 2.9, "V14": -8.5, "V16": -3.2,
            "V17": -5.1
        })
    elif is_suspicious_category and is_high_amount:
        # Moderate fraud signal
        feature_dict.update({
            "V1": -2.1, "V3": -2.4, "V4": 2.8,
            "V10": -2.9, "V14": -5.2, "V17": -3.1
        })
    elif is_suspicious_category:
        # Mild signal
        feature_dict.update({
            "V1": -1.2, "V3": -1.5, "V14": -2.8
        })

    # Override with any manually provided V features
    for col in feature_columns:
        val = getattr(transaction, col, None)
        if val is not None and val != 0.0:
            feature_dict[col] = val

    feature_dict['Amount']     = transaction.amount
    feature_dict['Time']       = transaction.Time
    feature_dict['Amount_log'] = np.log1p(transaction.amount)
    feature_dict['hour_of_day']= float(transaction.hour)
    feature_dict['is_night']   = 1.0 if (transaction.hour < 5 or transaction.hour > 22) else 0.0
    feature_dict['is_micro']   = 1.0 if (0 < transaction.amount < 1) else 0.0
    feature_dict['is_high']    = 1.0 if transaction.amount > 1000 else 0.0

    X = pd.DataFrame([feature_dict])[feature_columns]
    X[['Amount', 'Time', 'Amount_log']] = scaler.transform(
        X[['Amount', 'Time', 'Amount_log']]
    )

    # Isolation Forest score
    iso_raw   = iso_model.decision_function(X)[0]
    iso_score = 100 * (1 - (iso_raw + 0.5))
    iso_score = max(0, min(100, iso_score))

    # Best model score (XGBoost or RandomForest)
    rf_proba = best_model.predict_proba(X)[0][1] * 100

    # Rule-based score
    rule_score = 0
    if transaction.amount > 1000:   rule_score += 20
    elif transaction.amount > 500:  rule_score += 10
    if is_odd_hour:                 rule_score += 15
    if 0 < transaction.amount < 1:  rule_score += 25
    if transaction.merchant_category in ["Wire Transfer", "Crypto Exchange"]:
        rule_score += 15
    rule_score = min(rule_score, 100)

    # Behavioral score
    profile = user_profiles.get(transaction.user_id)
    behavioral_score = 0
    if profile:
        avg = profile['avg_amount']
        std = profile['std_amount'] if profile['std_amount'] > 0 else 1
        z   = abs(transaction.amount - avg) / std
        if z > 3:   behavioral_score += 30
        elif z > 2: behavioral_score += 20
        elif z > 1: behavioral_score += 10
        if transaction.hour not in profile['common_hours']:
            behavioral_score += 15
        if transaction.merchant_category not in profile['common_categories']:
            behavioral_score += 15
        behavioral_score = min(behavioral_score, 100)
    else:
        behavioral_score = 40

    # Final weighted score
    final_score = (
        0.55 * rf_proba +
        0.20 * iso_score +
        0.15 * rule_score +
        0.10 * behavioral_score
    )
    return round(min(final_score, 100), 2), round(rf_proba, 2), round(iso_score, 2), round(behavioral_score, 2)

def get_status(score):
    if score >= 65: return "FRAUD"
    elif score >= 35: return "SUSPICIOUS"
    return "SAFE"

def build_explanation(transaction, profile, is_odd_hour, is_suspicious_category,
                      velocity, reputation, rf_proba, iso_score, behavioral_score):
    reasons = []

    if rf_proba >= 60:
        reasons.append(f"🤖 ML model flagged high risk ({rf_proba:.0f}% fraud probability)")
    elif rf_proba >= 30:
        reasons.append(f"🤖 ML model detected moderate anomaly ({rf_proba:.0f}% fraud probability)")

    if is_odd_hour:
        reasons.append(f"🕐 Unusual hour ({transaction.hour:02d}:00 — outside normal banking hours)")

    if is_suspicious_category:
        reasons.append(f"⚠️ High-risk category: {transaction.merchant_category}")

    if transaction.amount > 1000:
        reasons.append(f"💸 High transaction amount (₹{transaction.amount:,.2f})")
    if 0 < transaction.amount < 1:
        reasons.append("🔍 Micro-transaction — possible card testing pattern")

    if profile:
        avg = profile['avg_amount']
        std = profile['std_amount'] if profile['std_amount'] > 0 else 1
        z   = abs(transaction.amount - avg) / std
        if z > 3:
            reasons.append(f"📊 Amount is {z:.1f}x above your normal spending (avg: ₹{avg:,.2f})")
        elif z > 2:
            reasons.append(f"📊 Amount significantly above your average (₹{avg:,.2f})")
        elif z > 1:
            reasons.append(f"📊 Amount slightly above your usual range (avg: ₹{avg:,.2f})")
        if transaction.hour not in profile['common_hours']:
            reasons.append("🕐 You don't usually transact at this hour")
        if transaction.merchant_category not in profile['common_categories']:
            reasons.append(f"🏪 Unusual category for your profile: {transaction.merchant_category}")
    else:
        reasons.append("👤 Unrecognised user profile — moderate risk applied")

    if velocity["triggered"]:
        reasons.append(f"⚡ Velocity alert: {velocity['reason']}")

    if reputation["is_blacklisted"]:
        reasons.append("🚫 Merchant is blacklisted")
    elif reputation["is_new"]:
        reasons.append("🆕 First transaction with this merchant")
    elif reputation["reason"]:
        reasons.append(f"🏪 Merchant history: {reputation['reason']}")

    if not reasons:
        reasons.append("✅ No significant risk factors detected")

    return reasons

# ══════════════════════════════════════════
#              ROUTES
# ══════════════════════════════════════════

@app.get("/")
def root():
    return {
        "system"   : "VaultSense — Secure Financial Monitoring",
        "version"  : "1.0.0",
        "status"   : "ONLINE",
        "endpoints": ["/analyze", "/blockchain/chain",
                      "/blockchain/validate", "/users/{user_id}", "/stats"]
    }

@app.post("/analyze")
def analyze_transaction(txn: TransactionInput):
    """Analyze a transaction and log it to the blockchain."""
    tx_counter["count"] += 1
    tx_id = f"TXN-{tx_counter['count']:05d}"

    risk_score, rf_proba, iso_score, behavioral_score = compute_risk_score(txn)

    # ── Merchant Reputation Check ──
    reputation       = check_merchant_reputation(txn.merchant)
    reputation_score = reputation["score"]

    # ── Log to in-memory velocity tracker ──
    velocity_log[txn.user_id].append({
        "amount"   : txn.amount,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "result"   : "APPROVED"
    })

    # ── Velocity Check ──
    velocity = check_velocity(txn.user_id, txn.amount, txn_log=velocity_log[txn.user_id])
    if velocity["triggered"]:
        # Blend velocity score into final risk
        risk_score = min(
            risk_score * 0.6 + velocity["velocity_score"] * 0.4,
            100
        )
        velocity_reason = velocity["reason"]
    else:
        velocity_reason = None

    # Blacklisted merchant = immediate FRAUD, no blending
    if reputation["is_blacklisted"]:
        risk_score = 95.0
        status     = "FRAUD"
    else:
        # Blend merchant reputation into final score
        risk_score = min(
            risk_score * 0.75 + reputation_score * 0.25,
            100
        )
        status = get_status(risk_score)

    # Update merchant stats after scoring
    update_merchant_stats(txn.merchant, status, txn.amount, txn.user_id)

    # Log to blockchain
    record = {
        "tx_id"             : tx_id,
        "user_id"           : txn.user_id,
        "amount"            : txn.amount,
        "merchant"          : txn.merchant,
        "merchant_category" : txn.merchant_category,
        "hour"              : txn.hour,
        "risk_score"        : risk_score,
        "status"            : status,
        "timestamp"         : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "velocity_triggered": velocity["triggered"],
        "velocity_reason"   : velocity_reason
    }
    block_hash = blockchain.add_transaction(record)

    explanation = build_explanation(
        transaction            = txn,
        profile                = user_profiles.get(txn.user_id),
        is_odd_hour            = txn.hour < 5 or txn.hour > 22,
        is_suspicious_category = txn.merchant_category in ["Wire Transfer", "Crypto Exchange", "ATM Withdrawal"],
        velocity               = velocity,
        reputation             = reputation,
        rf_proba               = rf_proba,
        iso_score              = iso_score,
        behavioral_score       = behavioral_score
    )

    return {
        "tx_id"              : tx_id,
        "risk_score"         : risk_score,
        "status"             : status,
        "block_hash"         : block_hash,
        "block_index"        : len(blockchain.chain) - 1,
        "timestamp"          : record["timestamp"],
        "velocity_triggered" : velocity["triggered"],
        "velocity_reason"    : velocity_reason,
        "merchant_reputation": reputation["reason"],
        "is_new_merchant"    : reputation["is_new"],
        "is_blacklisted"     : reputation["is_blacklisted"],
        "explanation"        : explanation,
        "message"            : "Transaction analyzed and recorded on blockchain."
    }

@app.get("/blockchain/chain")
def get_chain():
    """Return the full blockchain."""
    chain_data = []
    for block in blockchain.chain:
        chain_data.append({
            "index"        : block.index,
            "timestamp"    : block.timestamp,
            "transactions" : block.transactions,
            "hash"         : block.hash,
            "previous_hash": block.previous_hash,
            "nonce"        : block.nonce
        })
    return {"chain": chain_data, "length": len(chain_data)}

@app.get("/blockchain/validate")
def validate_chain():
    """Verify blockchain integrity."""
    is_valid = blockchain.is_chain_valid()
    return {
        "valid"   : is_valid,
        "blocks"  : len(blockchain.chain),
        "message" : "✅ Chain is intact." if is_valid else "❌ Chain has been tampered!"
    }

@app.get("/users/{user_id}")
def get_user_profile(user_id: str):
    """Get behavioral profile for a user."""
    profile = user_profiles.get(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found.")
    return profile

@app.get("/stats")
def get_stats():
    """Return system statistics."""
    return {
        "total_users"      : len(user_profiles),
        "blockchain_blocks": len(blockchain.chain),
        "chain_valid"      : blockchain.is_chain_valid(),
        "models_loaded"    : ["IsolationForest", "RandomForest", "RuleEngine", "BehavioralProfiler"],
        "system_status"    : "ONLINE"
    }
