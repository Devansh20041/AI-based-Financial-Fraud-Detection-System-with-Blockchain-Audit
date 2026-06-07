import streamlit as st
import requests
import hashlib
import random
import time
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.session_store import (
    register_user, get_user, add_transaction,
    add_alert, update_balance, get_transactions
)

# ── Page Config ──
st.set_page_config(
    page_title="AntiFraud MUJ — Banking",
    page_icon="🏦",
    layout="centered"
)

# ── Styling ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #040b14;
    color: #c8dff0;
}

/* Main background */
.stApp { background-color: #040b14; }

/* Cards */
.af-card {
    background: #07111f;
    border: 1px solid #0f2a45;
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 20px;
}

/* Title */
.af-title {
    font-family: 'Syne', sans-serif;
    font-size: 32px;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 4px;
}

.af-title span { color: #00d4ff; }

.af-subtitle {
    font-size: 13px;
    color: #3d6080;
    margin-bottom: 32px;
    font-family: monospace;
}

/* Balance card */
.balance-card {
    background: linear-gradient(135deg, #07111f, #0a1828);
    border: 1px solid #0f2a45;
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
}

.balance-label {
    font-size: 12px;
    color: #3d6080;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-family: monospace;
}

.balance-amount {
    font-family: 'Syne', sans-serif;
    font-size: 36px;
    font-weight: 800;
    color: #ffffff;
    margin: 4px 0;
}

.balance-acc {
    font-family: monospace;
    font-size: 12px;
    color: #3d6080;
}

/* Status badges */
.badge-safe {
    background: rgba(0,230,118,0.1);
    color: #00e676;
    border: 1px solid rgba(0,230,118,0.3);
    padding: 4px 14px;
    border-radius: 100px;
    font-size: 12px;
    font-family: monospace;
    font-weight: 700;
}

.badge-suspicious {
    background: rgba(255,184,0,0.1);
    color: #ffb800;
    border: 1px solid rgba(255,184,0,0.3);
    padding: 4px 14px;
    border-radius: 100px;
    font-size: 12px;
    font-family: monospace;
    font-weight: 700;
}

.badge-fraud {
    background: rgba(255,59,92,0.1);
    color: #ff3b5c;
    border: 1px solid rgba(255,59,92,0.3);
    padding: 4px 14px;
    border-radius: 100px;
    font-size: 12px;
    font-family: monospace;
    font-weight: 700;
}

/* Input styling */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div {
    background-color: #0a1828 !important;
    border: 1px solid #0f2a45 !important;
    color: #c8dff0 !important;
    border-radius: 8px !important;
}

/* Button */
.stButton > button {
    background: linear-gradient(135deg, #00d4ff, #0096ff) !important;
    color: #040b14 !important;
    font-weight: 700 !important;
    font-family: 'Syne', sans-serif !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 28px !important;
    font-size: 15px !important;
    width: 100% !important;
    transition: all 0.2s !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(0,212,255,0.3) !important;
}

/* Divider */
hr { border-color: #0f2a45 !important; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #07111f;
    border-radius: 10px;
    padding: 4px;
    border: 1px solid #0f2a45;
}

.stTabs [data-baseweb="tab"] {
    color: #3d6080;
    font-family: 'DM Sans', sans-serif;
}

.stTabs [aria-selected="true"] {
    background: #0a1828 !important;
    color: #00d4ff !important;
    border-radius: 8px !important;
}

/* Hide streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

BASE_URL = "http://127.0.0.1:8000"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_otp():
    return str(random.randint(100000, 999999))

def generate_account_no():
    return f"VS{random.randint(1000000000, 9999999999)}"

# ══════════════════════════════════════
#         SESSION STATE INIT
# ══════════════════════════════════════
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "otp_required" not in st.session_state:
    st.session_state.otp_required = False
if "otp_code" not in st.session_state:
    st.session_state.otp_code = None
if "pending_txn" not in st.session_state:
    st.session_state.pending_txn = None
if "page" not in st.session_state:
    st.session_state.page = "login"

# ══════════════════════════════════════
#         LOGIN / SIGNUP PAGE
# ══════════════════════════════════════
def show_auth():
    st.markdown("""
    <div style='text-align:center; padding: 40px 0 20px'>
        <div style='font-size:48px'>🏦</div>
        <div class='af-title' style='font-size:36px'>Vault<span>Sense</span></div>
        <div class='af-subtitle'>Secure Banking · AI Fraud Detection · Blockchain Verified</div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])

    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        username = st.text_input("Username", placeholder="Enter your username", key="login_user")
        password = st.text_input("Password", type="password", placeholder="Enter your password", key="login_pass")

        if st.button("Login →", key="login_btn"):
            if not username or not password:
                st.error("Please fill in all fields.")
            else:
                user = get_user(username)
                if not user:
                    st.error("❌ User not found. Please sign up first.")
                elif user["password"] != hash_password(password):
                    st.error("❌ Incorrect password.")
                else:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.session_state.page = "dashboard"
                    st.success(f"✅ Welcome back, {user['full_name']}!")
                    time.sleep(0.5)
                    st.rerun()

    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        full_name = st.text_input("Full Name", placeholder="John Doe", key="reg_name")
        new_user  = st.text_input("Username", placeholder="Choose a username", key="reg_user")
        new_pass  = st.text_input("Password", type="password", placeholder="Choose a password", key="reg_pass")
        conf_pass = st.text_input("Confirm Password", type="password", placeholder="Repeat password", key="reg_conf")

        if st.button("Create Account →", key="signup_btn"):
            if not all([full_name, new_user, new_pass, conf_pass]):
                st.error("Please fill in all fields.")
            elif new_pass != conf_pass:
                st.error("❌ Passwords do not match.")
            elif len(new_pass) < 6:
                st.error("❌ Password must be at least 6 characters.")
            elif get_user(new_user):
                st.error("❌ Username already exists.")
            else:
                acc_no = generate_account_no()
                success = register_user(new_user, hash_password(new_pass), full_name, acc_no)
                if success:
                    st.success(f"✅ Account created! Account No: **{acc_no}**")
                    st.info("Please login with your credentials.")
                else:
                    st.error("Registration failed. Try again.")

# ══════════════════════════════════════
#         MAIN BANKING DASHBOARD
# ══════════════════════════════════════
def show_dashboard():
    user = st.session_state.user

    # Reload fresh user data
    fresh = get_user(user["username"])
    if fresh:
        st.session_state.user = fresh
        user = fresh

    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"""
        <div class='af-title'>Vault<span>Sense</span></div>
        <div class='af-subtitle'>// Welcome, {user['full_name']} · Secure Banking Portal</div>
        """, unsafe_allow_html=True)
    with col2:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.page = "login"
            st.rerun()

    # Balance Card
    st.markdown(f"""
    <div class='balance-card'>
        <div class='balance-label'>Available Balance</div>
        <div class='balance-amount'>₹{user['balance']:,.2f}</div>
        <div class='balance-acc'>Account No: {user['account_no']} &nbsp;·&nbsp; VaultSense Bank</div>
    </div>
    """, unsafe_allow_html=True)

    # OTP Verification
    if st.session_state.otp_required:
        show_otp_screen()
        return

    # Tabs
    tab1, tab2 = st.tabs(["💸 Make Payment", "📋 Transaction History"])

    with tab1:
        show_payment_form()

    with tab2:
        show_history()

# ══════════════════════════════════════
#         PAYMENT FORM
# ══════════════════════════════════════
def show_payment_form():
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 💸 Send Payment")

    col1, col2 = st.columns(2)
    with col1:
        merchant = st.text_input("Merchant / Recipient", placeholder="e.g. Amazon, John Doe")
        amount   = st.number_input("Amount (₹)", min_value=1.0, max_value=100000.0,
                                   value=500.0, step=100.0)
    with col2:
        category = st.selectbox("Category", [
            "Food & Beverage", "E-Commerce", "Travel",
            "Entertainment", "Utilities", "Healthcare",
            "Retail", "Wire Transfer", "Crypto Exchange",
            "ATM Withdrawal", "Education", "Other"
        ])
        location = st.selectbox("Location", [
            "Jaipur", "Delhi", "Mumbai", "Bangalore",
            "Hyderabad", "Chennai", "Overseas", "Unknown"
        ])

    hour = datetime.now().hour
    st.markdown(f"<div style='font-size:12px;color:#3d6080;margin-bottom:8px;font-family:monospace'>🕐 Transaction time: {hour:02d}:00 (current hour detected automatically)</div>", unsafe_allow_html=True)

    note = st.text_input("Note (optional)", placeholder="e.g. Monthly rent, Birthday gift...")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚀 Send Payment"):
        if not merchant:
            st.error("Please enter a merchant name.")
            return

        user = st.session_state.user
        if amount > user["balance"]:
            st.error("❌ Insufficient balance.")
            return

        with st.spinner("🔍 VaultSense AI is analyzing your transaction..."):
            time.sleep(1.2)
            payload = {
                "user_id"           : user["username"],
                "amount"            : float(amount),
                "merchant"          : merchant,
                "merchant_category" : category,
                "hour"              : hour,
            }

            try:
                r = requests.post(f"{BASE_URL}/analyze", json=payload, timeout=10)
                result = r.json()
            except Exception as e:
                st.error(f"API Error: {e}")
                return

        risk_score = result.get("risk_score", 0)
        status     = result.get("status", "SAFE")
        tx_id      = result.get("tx_id", "N/A")
        block_hash = result.get("block_hash", "N/A")

        # Save to session store
        txn_record = {
            "tx_id"      : tx_id,
            "user"       : user["username"],
            "merchant"   : merchant,
            "category"   : category,
            "location"   : location,
            "amount"     : float(amount),
            "hour"       : hour,
            "risk_score" : risk_score,
            "status"     : status,
            "block_hash" : block_hash,
            "note"       : note,
            "timestamp"  : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        if status == "FRAUD":
            add_alert({
                "type"      : "FRAUD",
                "tx_id"     : tx_id,
                "user"      : user["username"],
                "amount"    : float(amount),
                "merchant"  : merchant,
                "risk_score": risk_score,
                "velocity_reason" : result.get("velocity_reason"),
                "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            add_transaction({**txn_record, "result": "BLOCKED"})
            st.error(f"""
            🚨 **Transaction BLOCKED**

            VaultSense AI detected this transaction as potentially fraudulent.

            - Risk Score: **{risk_score:.1f}/100**
            - TX ID: `{tx_id}`
            - Block Hash: `{block_hash[:24]}...`

            This transaction has been logged and reported to the security team.
            """)
            explanation = result.get("explanation", [])
            if explanation:
                with st.expander("🔍 Why was this blocked?"):
                    for reason in explanation:
                        st.markdown(f"- {reason}")

        elif status == "SUSPICIOUS":
            add_alert({
                "type"      : "SUSPICIOUS",
                "tx_id"     : tx_id,
                "user"      : user["username"],
                "amount"    : float(amount),
                "merchant"  : merchant,
                "risk_score": risk_score,
                "velocity_reason" : result.get("velocity_reason"),
                "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            st.session_state.otp_required = True
            st.session_state.otp_code     = generate_otp()
            st.session_state.pending_txn  = txn_record
            explanation = result.get("explanation", [])
            st.warning(f"""
            ⚠️ **Verification Required**

            This transaction looks unusual. Risk Score: **{risk_score:.1f}/100**

            An OTP has been sent to your registered mobile number.
            """)
            if explanation:
                with st.expander("🔍 Why was this flagged?"):
                    for reason in explanation:
                        st.markdown(f"- {reason}")
            time.sleep(1)
            st.rerun()

        else:
            add_transaction({**txn_record, "result": "APPROVED"})
            update_balance(user["username"], amount)
            st.session_state.user = get_user(user["username"])
            st.success(f"""
            ✅ **Payment Successful!**

            - Amount: **₹{amount:,.2f}** to **{merchant}**
            - Risk Score: **{risk_score:.1f}/100** (Safe)
            - TX ID: `{tx_id}`
            - Blockchain: `{block_hash[:24]}...`
            """)
            explanation = result.get("explanation", [])
            if explanation:
                with st.expander("🔍 Why this risk score?"):
                    for reason in explanation:
                        st.markdown(f"- {reason}")

# ══════════════════════════════════════
#         OTP SCREEN
# ══════════════════════════════════════
def show_otp_screen():
    st.markdown("---")
    st.markdown("### 🔐 Verification Required")

    txn = st.session_state.pending_txn
    real_otp = st.session_state.otp_code

    st.warning(f"""
    ⚠️ Unusual transaction detected!

    **Merchant:** {txn['merchant']}
    **Amount:** ₹{txn['amount']:,.2f}
    **Risk Score:** {txn['risk_score']:.1f}/100

    Enter the OTP sent to your registered mobile to proceed.
    """)

    # Show OTP hint for demo
    st.info(f"📱 Demo OTP (for presentation): **{real_otp}**")

    entered_otp = st.text_input("Enter OTP", placeholder="6-digit OTP", max_chars=6)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Verify & Proceed"):
            if entered_otp == real_otp:
                add_transaction({**txn, "result": "APPROVED (OTP Verified)"})
                update_balance(txn["user"], txn["amount"])
                st.session_state.otp_required = False
                st.session_state.otp_code     = None
                st.session_state.pending_txn  = None
                st.session_state.user = get_user(txn["user"])
                st.success("✅ OTP Verified! Transaction approved.")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ Incorrect OTP. Please try again.")

    with col2:
        if st.button("❌ Cancel Transaction"):
            add_transaction({**txn, "result": "CANCELLED by user"})
            st.session_state.otp_required = False
            st.session_state.otp_code     = None
            st.session_state.pending_txn  = None
            st.warning("Transaction cancelled.")
            time.sleep(1)
            st.rerun()

# ══════════════════════════════════════
#         TRANSACTION HISTORY
# ══════════════════════════════════════
def show_history():
    st.markdown("<br>", unsafe_allow_html=True)
    user = st.session_state.user
    all_txns = get_transactions()
    my_txns  = [t for t in all_txns if t.get("user") == user["username"]]

    if not my_txns:
        st.info("No transactions yet. Make your first payment!")
        return

    st.markdown(f"**{len(my_txns)} transactions found**")

    for txn in my_txns:
        status = txn.get("status", "SAFE")
        result = txn.get("result", "")
        badge  = {
            "FRAUD"     : "🚨 FRAUD",
            "SUSPICIOUS": "⚠️ SUSPICIOUS",
            "SAFE"      : "✅ SAFE"
        }.get(status, "✅ SAFE")

        with st.expander(f"{badge} &nbsp;·&nbsp; ₹{txn['amount']:,.2f} → {txn['merchant']} &nbsp;·&nbsp; {txn['timestamp']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**TX ID:** `{txn.get('tx_id','N/A')}`")
                st.markdown(f"**Category:** {txn.get('category','N/A')}")
                st.markdown(f"**Location:** {txn.get('location','N/A')}")
                st.markdown(f"**Result:** {result}")
            with col2:
                st.markdown(f"**Risk Score:** {txn.get('risk_score',0):.1f}/100")
                st.markdown(f"**Block Hash:** `{txn.get('block_hash','N/A')[:20]}...`")
                st.markdown(f"**Note:** {txn.get('note','—')}")

# ══════════════════════════════════════
#         ROUTER
# ══════════════════════════════════════
if not st.session_state.logged_in:
    show_auth()
else:
    show_dashboard()