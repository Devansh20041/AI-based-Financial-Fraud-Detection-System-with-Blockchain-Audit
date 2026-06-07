import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
import pickle

if __name__ == "__main__":
    # ── 1. LOAD DATA ──
    print("📂 Loading dataset for behavioral profiling...")
    _HERE = os.path.dirname(os.path.abspath(__file__))
    _ROOT = os.path.dirname(_HERE)
    df = pd.read_csv(os.path.join(_ROOT, "data", "creditcard.csv"))

    # Simulate user IDs
    np.random.seed(42)
    num_users = 500
    df['user_id'] = np.random.choice([f"USR-{str(i).zfill(4)}" for i in range(1, num_users+1)], size=len(df))

    # Simulate merchant categories
    categories = ['Food & Beverage', 'E-Commerce', 'Travel', 'Entertainment',
                  'Utilities', 'Healthcare', 'Retail', 'Wire Transfer',
                  'Crypto Exchange', 'ATM Withdrawal']
    df['merchant_category'] = np.random.choice(categories, size=len(df))

    # Simulate hour of day from Time column
    df['hour'] = ((df['Time'] % 86400) / 3600).astype(int)

    print(f"✅ Loaded {len(df):,} transactions across {num_users} users")

    # ── 2. BUILD BEHAVIORAL PROFILES ──
    print("\n👤 Building user behavioral profiles...")

    profiles = {}

    for user_id, group in df.groupby('user_id'):
        txns = group.copy()

        avg_amount  = txns['Amount'].mean()
        std_amount  = txns['Amount'].std() if len(txns) > 1 else 0
        max_amount  = txns['Amount'].max()
        min_amount  = txns['Amount'].min()
        total_spent = txns['Amount'].sum()
        txn_count   = len(txns)

        common_hours = txns['hour'].value_counts().head(3).index.tolist()
        common_cats  = txns['merchant_category'].value_counts().head(3).index.tolist()
        fraud_count  = txns['Class'].sum()
        fraud_rate   = fraud_count / txn_count if txn_count > 0 else 0

        if fraud_rate > 0.05 or avg_amount > 500:
            risk_level = "HIGH"
        elif fraud_rate > 0.01 or avg_amount > 200:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        profiles[user_id] = {
            "user_id"           : user_id,
            "transaction_count" : int(txn_count),
            "avg_amount"        : round(float(avg_amount), 2),
            "std_amount"        : round(float(std_amount), 2),
            "max_amount"        : round(float(max_amount), 2),
            "min_amount"        : round(float(min_amount), 2),
            "total_spent"       : round(float(total_spent), 2),
            "common_hours"      : common_hours,
            "common_categories" : common_cats,
            "fraud_count"       : int(fraud_count),
            "fraud_rate"        : round(float(fraud_rate), 4),
            "risk_level"        : risk_level,
            "last_updated"      : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    print(f"✅ Built profiles for {len(profiles)} users")

    # ── 3. ANOMALY DETECTOR ──
    def is_anomalous_for_user(user_id, amount, hour, category):
        if user_id not in profiles:
            return 50
        p     = profiles[user_id]
        score = 0
        if p['std_amount'] > 0:
            z_score = abs(amount - p['avg_amount']) / p['std_amount']
            if z_score > 3:   score += 40
            elif z_score > 2: score += 25
            elif z_score > 1: score += 10
        if hour not in p['common_hours']:
            score += 20
        if category not in p['common_categories']:
            score += 20
        if amount > p['max_amount'] * 1.5:
            score += 20
        return min(int(score), 100)

    # ── 4. TEST ──
    print("\n🧪 Testing behavioral anomaly detection...")
    print("-" * 55)
    test_cases = [
        ("USR-0001", 25.00,   10, "Food & Beverage", "Normal purchase"),
        ("USR-0001", 9999.00,  3, "Wire Transfer",   "Suspicious wire"),
        ("USR-0042", 150.00,  14, "E-Commerce",      "Normal online shop"),
        ("USR-0042", 5000.00,  2, "Crypto Exchange", "Late night crypto"),
        ("USR-0100", 1.00,    23, "ATM Withdrawal",  "Card testing?"),
    ]
    for user, amount, hour, category, desc in test_cases:
        deviation = is_anomalous_for_user(user, amount, hour, category)
        flag = "🚨 HIGH" if deviation >= 60 else "⚠️  MED " if deviation >= 30 else "✅ LOW "
        print(f"  {flag} | {user} | ₹{amount:>8.2f} | {category:<20} | Score: {deviation:>3} | {desc}")
    print("-" * 55)

    # ── 5. PROFILE SUMMARY ──
    print("\n📊 Profile Summary:")
    risk_counts = pd.Series([p['risk_level'] for p in profiles.values()]).value_counts()
    print(f"   🔴 HIGH risk users   : {risk_counts.get('HIGH', 0)}")
    print(f"   🟡 MEDIUM risk users : {risk_counts.get('MEDIUM', 0)}")
    print(f"   🟢 LOW risk users    : {risk_counts.get('LOW', 0)}")

    # ── 6. SAVE ──
    print("\n💾 Saving profiles...")
    PROFILE_OUT = os.path.join(_HERE, "user_profiles.json")
    os.makedirs(_HERE, exist_ok=True)

    with open(PROFILE_OUT, 'w') as f:
        json.dump(profiles, f, indent=2)

    print(f"✅ Saved → {PROFILE_OUT}")
    print(f"\n🎉 Behavioral Profiling complete! {len(profiles)} user profiles ready.")