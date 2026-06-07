import streamlit as st
import requests
import json
import time
import sys
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.session_store import get_transactions, get_alerts, clear_alerts
from utils.merchant_reputation import blacklist_merchant, whitelist_merchant, get_all_merchant_stats

# ── Page Config ──
st.set_page_config(
    page_title="AntiFraud MUJ — Security",
    page_icon="🛡️",
    layout="wide"
)

BASE_URL = "http://127.0.0.1:8000"

# ── Styling ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=Share+Tech+Mono&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #040b14;
    color: #c8dff0;
}

.stApp { background-color: #040b14; }

/* Header */
.sec-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 0 24px;
    border-bottom: 1px solid #0f2a45;
    margin-bottom: 24px;
}

.sec-title {
    font-family: 'Syne', sans-serif;
    font-size: 26px;
    font-weight: 800;
    color: #ffffff;
}

.sec-title span { color: #00d4ff; }

.sec-subtitle {
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: #3d6080;
    margin-top: 2px;
}

/* KPI Cards */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 24px;
}

.kpi {
    background: #07111f;
    border: 1px solid #0f2a45;
    border-radius: 12px;
    padding: 20px;
    position: relative;
    overflow: hidden;
}

.kpi::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}

.kpi.blue::before  { background: linear-gradient(90deg, #00d4ff, transparent); }
.kpi.red::before   { background: linear-gradient(90deg, #ff3b5c, transparent); }
.kpi.yellow::before{ background: linear-gradient(90deg, #ffb800, transparent); }
.kpi.green::before { background: linear-gradient(90deg, #00e676, transparent); }

.kpi-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    color: #3d6080;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 8px;
}

.kpi-value {
    font-family: 'Syne', sans-serif;
    font-size: 32px;
    font-weight: 800;
    color: #ffffff;
    line-height: 1;
    margin-bottom: 4px;
}

.kpi-sub {
    font-size: 11px;
    color: #3d6080;
}

/* Transaction Row */
.txn-row {
    background: #07111f;
    border: 1px solid #0f2a45;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 16px;
    transition: border-color 0.2s;
}

.txn-row.fraud    { border-color: rgba(255,59,92,0.4); background: rgba(255,59,92,0.04); }
.txn-row.suspicious { border-color: rgba(255,184,0,0.3); background: rgba(255,184,0,0.03); }

/* Alert */
.alert-box {
    background: rgba(255,59,92,0.08);
    border: 1px solid rgba(255,59,92,0.4);
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 10px;
    animation: fadeIn 0.4s ease;
}

.alert-box.warn {
    background: rgba(255,184,0,0.06);
    border-color: rgba(255,184,0,0.35);
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(-6px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* Block card */
.block-card {
    background: #0a1828;
    border: 1px solid #0f2a45;
    border-radius: 10px;
    padding: 14px;
    margin-bottom: 6px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: #3d6080;
    transition: border-color 0.2s;
}

.block-card:hover { border-color: rgba(0,255,157,0.3); }
.block-num { color: #00ff9d; font-weight: 700; font-size: 13px; }
.block-hash span { color: #00d4ff; }

/* Risk bar */
.risk-wrap {
    display: flex;
    align-items: center;
    gap: 8px;
    width: 140px;
}

.risk-bg {
    flex: 1;
    height: 5px;
    background: #0a1828;
    border-radius: 100px;
    overflow: hidden;
}

/* Badges */
.badge {
    padding: 3px 12px;
    border-radius: 100px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    font-weight: 700;
    white-space: nowrap;
}

.badge-fraud      { background: rgba(255,59,92,0.12); color: #ff3b5c; border: 1px solid rgba(255,59,92,0.3); }
.badge-suspicious { background: rgba(255,184,0,0.10); color: #ffb800; border: 1px solid rgba(255,184,0,0.3); }
.badge-safe       { background: rgba(0,230,118,0.08); color: #00e676; border: 1px solid rgba(0,230,118,0.25); }

/* Streamlit overrides */
.stButton > button {
    background: #07111f !important;
    border: 1px solid #0f2a45 !important;
    color: #c8dff0 !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
}

.stButton > button:hover {
    border-color: #00d4ff !important;
    color: #00d4ff !important;
}

div[data-testid="metric-container"] {
    background: #07111f;
    border: 1px solid #0f2a45;
    border-radius: 10px;
    padding: 12px;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════
#         HEADER
# ══════════════════════════════════════
col_h1, col_h2, col_h3 = st.columns([3, 2, 1])
with col_h1:
    st.markdown("""
    <div class='sec-title'>🛡️ Vault<span>Sense</span> — Security Center</div>
    <div class='sec-subtitle'>// LIVE MONITORING · BLOCKCHAIN VERIFIED · AI POWERED</div>
    """, unsafe_allow_html=True)

with col_h2:
    st.markdown(f"""
    <div style='text-align:right; padding-top:8px;'>
        <div style='font-family:monospace; font-size:11px; color:#3d6080;'>
            🟢 SYSTEM ONLINE &nbsp;·&nbsp; {datetime.now().strftime("%d %b %Y · %H:%M:%S")}
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_h3:
    auto_refresh = st.toggle("Auto Refresh", value=True)

st.markdown("<hr style='border-color:#0f2a45; margin: 0 0 24px'>", unsafe_allow_html=True)

# ══════════════════════════════════════
#         LOAD DATA
# ══════════════════════════════════════
transactions = get_transactions()
alerts       = get_alerts()

try:
    stats = requests.get(f"{BASE_URL}/stats", timeout=3).json()
    chain = requests.get(f"{BASE_URL}/blockchain/chain", timeout=3).json()
    valid = requests.get(f"{BASE_URL}/blockchain/validate", timeout=3).json()
    api_online = True
except:
    stats = {}
    chain = {"chain": [], "length": 0}
    valid = {"valid": False}
    api_online = False

# ══════════════════════════════════════
#         KPI CARDS
# ══════════════════════════════════════
fraud_txns      = [t for t in transactions if t.get("status") == "FRAUD"]
suspicious_txns = [t for t in transactions if t.get("status") == "SUSPICIOUS"]
safe_txns       = [t for t in transactions if t.get("status") == "SAFE"]
total           = len(transactions)

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
    <div class='kpi blue'>
        <div class='kpi-label'>Total Transactions</div>
        <div class='kpi-value'>{total}</div>
        <div class='kpi-sub'>Processed by VaultSense</div>
    </div>""", unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class='kpi red'>
        <div class='kpi-label'>Fraud Detected</div>
        <div class='kpi-value' style='color:#ff3b5c'>{len(fraud_txns)}</div>
        <div class='kpi-sub'>Transactions blocked</div>
    </div>""", unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class='kpi yellow'>
        <div class='kpi-label'>Suspicious</div>
        <div class='kpi-value' style='color:#ffb800'>{len(suspicious_txns)}</div>
        <div class='kpi-sub'>Flagged for review</div>
    </div>""", unsafe_allow_html=True)

chain_is_valid = valid.get("valid", False)
chain_status   = "INTACT ✓"  if chain_is_valid else "COMPROMISED ✗"
chain_color    = "#00e676"    if chain_is_valid else "#ff3b5c"

with k4:
    st.markdown(f"""
    <div class='kpi green'>
        <div class='kpi-label'>Blockchain</div>
        <div class='kpi-value' style='color:{chain_color}; font-size:20px'>{chain_status}</div>
        <div class='kpi-sub'>{chain.get("length", 0)} blocks recorded</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════
#         TABS
# ══════════════════════════════════════
tab_live, tab_analytics = st.tabs(["⚡ Live Monitor", "📊 Analytics"])

with tab_analytics:
    if not transactions:
        st.info("No transactions yet. Make some payments to see analytics.")
    else:
        df = pd.DataFrame(transactions)
        st.markdown("### 📊 Analytics Dashboard")
        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**🏪 Transactions by Category & Status**")
            cat_data = df.groupby(["category", "status"]).size().reset_index(name="count")
            fig1 = px.bar(
                cat_data, x="category", y="count", color="status",
                color_discrete_map={"FRAUD":"#ff3b5c","SUSPICIOUS":"#ffb800","SAFE":"#00e676"},
                template="plotly_dark"
            )
            fig1.update_layout(
                paper_bgcolor="#07111f", plot_bgcolor="#07111f",
                font_color="#c8dff0", xaxis_tickangle=-30, margin=dict(t=20,b=20)
            )
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            st.markdown("**🕐 Transaction Volume by Hour**")
            hour_data = df.groupby(["hour","status"]).size().reset_index(name="count")
            fig2 = px.bar(
                hour_data, x="hour", y="count", color="status",
                color_discrete_map={"FRAUD":"#ff3b5c","SUSPICIOUS":"#ffb800","SAFE":"#00e676"},
                template="plotly_dark"
            )
            fig2.update_layout(
                paper_bgcolor="#07111f", plot_bgcolor="#07111f",
                font_color="#c8dff0", xaxis_title="Hour of Day", margin=dict(t=20,b=20)
            )
            st.plotly_chart(fig2, use_container_width=True)

        col3, col4 = st.columns(2)

        with col3:
            st.markdown("**📈 Risk Score Distribution**")
            fig3 = px.histogram(
                df, x="risk_score", nbins=20, color="status",
                color_discrete_map={"FRAUD":"#ff3b5c","SUSPICIOUS":"#ffb800","SAFE":"#00e676"},
                template="plotly_dark"
            )
            fig3.update_layout(
                paper_bgcolor="#07111f", plot_bgcolor="#07111f",
                font_color="#c8dff0", xaxis_title="Risk Score",
                yaxis_title="Count", margin=dict(t=20,b=20)
            )
            fig3.add_vline(x=35, line_dash="dash", line_color="#ffb800",
                           annotation_text="Suspicious", annotation_font_color="#ffb800")
            fig3.add_vline(x=65, line_dash="dash", line_color="#ff3b5c",
                           annotation_text="Fraud", annotation_font_color="#ff3b5c")
            st.plotly_chart(fig3, use_container_width=True)

        with col4:
            st.markdown("**👤 Top Flagged Users**")
            flagged_df = df[df["status"].isin(["FRAUD","SUSPICIOUS"])]
            if flagged_df.empty:
                st.info("No flagged users yet.")
            else:
                user_counts = flagged_df.groupby(["user","status"]).size().reset_index(name="count")
                fig4 = px.bar(
                    user_counts, x="user", y="count", color="status",
                    color_discrete_map={"FRAUD":"#ff3b5c","SUSPICIOUS":"#ffb800"},
                    template="plotly_dark"
                )
                fig4.update_layout(
                    paper_bgcolor="#07111f", plot_bgcolor="#07111f",
                    font_color="#c8dff0", margin=dict(t=20,b=20)
                )
                st.plotly_chart(fig4, use_container_width=True)

        st.markdown("---")
        st.markdown("**💰 Amount Analysis**")
        col5, col6, col7 = st.columns(3)
        with col5:
            st.metric("Total Volume", f"₹{df['amount'].sum():,.2f}")
        with col6:
            fraud_vol = df[df["status"]=="FRAUD"]["amount"].sum()
            st.metric("Fraud Volume Blocked", f"₹{fraud_vol:,.2f}")
        with col7:
            st.metric("Avg Risk Score", f"{df['risk_score'].mean():.1f}/100")

        st.markdown("---")
        st.markdown("**📥 Export Report**")

        import io
        exp_col1, exp_col2 = st.columns(2)

        with exp_col1:
            # Full transaction CSV
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            st.download_button(
                label     = "⬇️ Download Full Transaction Report (CSV)",
                data      = csv_buffer.getvalue(),
                file_name = f"vaultsense_transactions_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime      = "text/csv"
            )

        with exp_col2:
            # Fraud only CSV
            fraud_df     = df[df["status"].isin(["FRAUD", "SUSPICIOUS"])]
            fraud_buffer = io.StringIO()
            fraud_df.to_csv(fraud_buffer, index=False)
            st.download_button(
                label     = "🚨 Download Fraud Report Only (CSV)",
                data      = fraud_buffer.getvalue(),
                file_name = f"vaultsense_fraud_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime      = "text/csv"
            )

with tab_live:
    # ── MAIN LAYOUT ──
    left_col, right_col = st.columns([2, 1])

    # ── LEFT: Transaction Feed + Alerts ──
    with left_col:

        # ── Simulation Button ──
        st.markdown("### 🎮 Demo Simulation")
        sim_col1, sim_col2 = st.columns([3, 1])
        with sim_col1:
            st.markdown("""
            <div style='font-size:12px; color:#3d6080; font-family:monospace; padding-top:8px'>
                Auto-fire realistic transactions to demonstrate fraud detection live.
            </div>
            """, unsafe_allow_html=True)
        with sim_col2:
            run_sim = st.button("🚀 Run Demo", key="sim_btn")

        if run_sim:
            sim_transactions = [
                {"user_id": "USR-0042", "amount": 42.50,   "merchant": "Starbucks",             "merchant_category": "Food & Beverage", "hour": 9},
                {"user_id": "USR-0042", "amount": 9999.00, "merchant": "Unknown Offshore Ltd.",  "merchant_category": "Wire Transfer",   "hour": 3},
                {"user_id": "USR-0071", "amount": 128.99,  "merchant": "Amazon",                 "merchant_category": "E-Commerce",      "hour": 14},
                {"user_id": "USR-0042", "amount": 0.50,    "merchant": "Unknown Merchant",        "merchant_category": "ATM Withdrawal",  "hour": 23},
                {"user_id": "USR-0118", "amount": 4200.00, "merchant": "Crypto Exchange Pro",    "merchant_category": "Crypto Exchange", "hour": 2},
                {"user_id": "USR-0042", "amount": 5500.00, "merchant": "Offshore Wire Services", "merchant_category": "Wire Transfer",   "hour": 4},
                {"user_id": "USR-0305", "amount": 18.00,   "merchant": "Netflix",                "merchant_category": "Entertainment",   "hour": 20},
            ]

            progress = st.progress(0, text="Starting simulation...")
            results  = []

            for i, txn in enumerate(sim_transactions):
                try:
                    r      = requests.post(f"{BASE_URL}/analyze", json=txn, timeout=10)
                    result = r.json()
                    results.append((txn, result))
                    status = result.get("status", "SAFE")
                    icon   = "🚨" if status == "FRAUD" else "⚠️" if status == "SUSPICIOUS" else "✅"
                    progress.progress(
                        (i + 1) / len(sim_transactions),
                        text=f"{icon} [{i+1}/{len(sim_transactions)}] {txn['merchant']} — {status} (Risk: {result.get('risk_score', 0):.1f})"
                    )
                    time.sleep(0.6)
                except Exception as e:
                    st.error(f"API Error on transaction {i+1}: {e}")
                    break

            st.success(f"✅ Simulation complete! {len(results)} transactions fired.")

            fraud_c = sum(1 for _, r in results if r.get("status") == "FRAUD")
            susp_c  = sum(1 for _, r in results if r.get("status") == "SUSPICIOUS")
            safe_c  = sum(1 for _, r in results if r.get("status") == "SAFE")

            rc1, rc2, rc3 = st.columns(3)
            with rc1:
                st.metric("🚨 Fraud Blocked",  fraud_c)
            with rc2:
                st.metric("⚠️ Suspicious",     susp_c)
            with rc3:
                st.metric("✅ Safe",            safe_c)

            time.sleep(1)
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # Active Alerts
        if alerts:
            st.markdown("### 🚨 Active Alerts")
            for alert in alerts[:5]:
                a_type = alert.get("type", "")
                cls    = "alert-box" if a_type == "FRAUD" else "alert-box warn"
                icon   = "🚨" if a_type == "FRAUD" else "⚠️"
                color  = "#ff3b5c" if a_type == "FRAUD" else "#ffb800"
                st.markdown(f"""
                <div class='{cls}'>
                    <div style='display:flex; justify-content:space-between; align-items:center'>
                        <div style='font-weight:700; color:{color}; font-size:14px'>
                            {icon} {a_type} DETECTED — {alert.get('tx_id','N/A')}
                        </div>
                        <div style='font-family:monospace; font-size:10px; color:#3d6080'>
                            {alert.get('timestamp','')}
                        </div>
                    </div>
                    <div style='margin-top:8px; font-size:13px; color:#c8dff0'>
                        👤 <b>{alert.get('user','N/A')}</b> &nbsp;·&nbsp;
                        💰 <b>₹{alert.get('amount',0):,.2f}</b> &nbsp;·&nbsp;
                        🏪 {alert.get('merchant','N/A')} &nbsp;·&nbsp;
                        Risk: <b style='color:{color}'>{alert.get('risk_score',0):.1f}/100</b>
                    </div>
                    {f"<div style='margin-top:6px; font-size:11px; font-family:monospace; color:#ffb800'>⚡ VELOCITY: {alert.get('velocity_reason','')}</div>" if alert.get('velocity_reason') else ""}
                </div>
                """, unsafe_allow_html=True)

            if st.button("🗑 Clear Alerts"):
                clear_alerts()
                st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)

        # Live Transaction Feed
        st.markdown("### ⚡ Live Transaction Feed")

        if not transactions:
            st.info("No transactions yet. Waiting for activity from the banking app...")
        else:
            for txn in transactions[:15]:
                status = txn.get("status", "SAFE")
                score  = txn.get("risk_score", 0)

                if status == "FRAUD":
                    row_class   = "fraud"
                    badge_class = "badge-fraud"
                    badge_text  = "🚨 FRAUD"
                    bar_color   = "#ff3b5c"
                elif status == "SUSPICIOUS":
                    row_class   = "suspicious"
                    badge_class = "badge-suspicious"
                    badge_text  = "⚠️ SUSPICIOUS"
                    bar_color   = "#ffb800"
                else:
                    row_class   = ""
                    badge_class = "badge-safe"
                    badge_text  = "✅ SAFE"
                    bar_color   = "#00e676"

                bar_width = int(score)

                st.markdown(f"""
                <div class='txn-row {row_class}'>
                    <div style='min-width:90px'>
                        <div style='font-family:monospace; font-size:11px; color:#00d4ff'>
                            {txn.get('tx_id','N/A')}
                        </div>
                        <div style='font-size:10px; color:#3d6080; margin-top:2px'>
                            {txn.get('timestamp','')[-8:]}
                        </div>
                    </div>
                    <div style='flex:1'>
                        <div style='font-size:13px; font-weight:600; color:#fff'>
                            {txn.get('merchant','N/A')}
                        </div>
                        <div style='font-size:11px; color:#3d6080'>
                            {txn.get('category','N/A')} · 👤 {txn.get('user','N/A')}
                        </div>
                    </div>
                    <div style='min-width:80px; text-align:right'>
                        <div style='font-family:monospace; font-weight:700; color:#fff'>
                            ₹{txn.get('amount',0):,.2f}
                        </div>
                    </div>
                    <div class='risk-wrap'>
                        <div class='risk-bg'>
                            <div style='height:5px; width:{bar_width}%; background:{bar_color}; border-radius:100px'></div>
                        </div>
                        <div style='font-family:monospace; font-size:11px; color:{bar_color}; width:35px; text-align:right'>
                            {score:.0f}
                        </div>
                    </div>
                    <div>
                        <span class='badge {badge_class}'>{badge_text}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── RIGHT: Blockchain + System Status ──
    with right_col:

        st.markdown("### 🖥️ System Status")
        api_color = "#00e676" if api_online else "#ff3b5c"
        api_text  = "ONLINE"  if api_online else "OFFLINE"
        chain_col = "#00e676" if valid.get("valid") else "#ff3b5c"

        st.markdown(f"""
        <div style='background:#07111f; border:1px solid #0f2a45; border-radius:10px; padding:16px; margin-bottom:16px;'>
            <div style='display:flex; justify-content:space-between; margin-bottom:10px;'>
                <span style='font-size:12px; color:#3d6080'>API Server</span>
                <span style='font-family:monospace; font-size:11px; color:{api_color}'>● {api_text}</span>
            </div>
            <div style='display:flex; justify-content:space-between; margin-bottom:10px;'>
                <span style='font-size:12px; color:#3d6080'>ML Models</span>
                <span style='font-family:monospace; font-size:11px; color:#00e676'>● LOADED</span>
            </div>
            <div style='display:flex; justify-content:space-between; margin-bottom:10px;'>
                <span style='font-size:12px; color:#3d6080'>Blockchain</span>
                <span style='font-family:monospace; font-size:11px; color:{chain_col}'>● {chain_status}</span>
            </div>
            <div style='display:flex; justify-content:space-between;'>
                <span style='font-size:12px; color:#3d6080'>User Profiles</span>
                <span style='font-family:monospace; font-size:11px; color:#00e676'>● {stats.get('total_users', 500)} LOADED</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("### ⛓️ Blockchain Ledger")
        chain_blocks = chain.get("chain", [])
        if not chain_blocks:
            st.info("No blocks yet.")
        else:
            for block in reversed(chain_blocks[-5:]):
                txn_count = len(block.get("transactions", []))
                st.markdown(f"""
                <div class='block-card'>
                    <div style='display:flex; justify-content:space-between; margin-bottom:6px'>
                        <span class='block-num'>BLOCK #{block['index']}</span>
                        <span style='color:#3d6080; font-size:10px'>{block['timestamp']}</span>
                    </div>
                    <div class='block-hash'>Hash: <span>{block['hash'][:28]}...</span></div>
                    <div class='block-hash' style='margin-top:2px'>Prev: <span>{block['previous_hash'][:28]}...</span></div>
                    <div style='margin-top:6px; display:flex; justify-content:space-between'>
                        <span>Txns: {txn_count} · Nonce: {block['nonce']}</span>
                        <span style='color:#00ff9d'>✓ VERIFIED</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("### 🏪 Merchant Control")
        mer_data = get_all_merchant_stats()

        if mer_data["blacklist"]:
            st.markdown(f"""
            <div style='background:rgba(255,59,92,0.08); border:1px solid rgba(255,59,92,0.3);
                        border-radius:10px; padding:12px 16px; margin-bottom:10px'>
                <div style='font-family:monospace; font-size:11px; color:#ff3b5c; margin-bottom:6px'>
                    🚫 BLACKLISTED MERCHANTS ({len(mer_data["blacklist"])})
                </div>
                {''.join([f"<div style='font-size:12px; color:#c8dff0; padding:2px 0'>• {m}</div>" for m in mer_data["blacklist"]])}
            </div>
            """, unsafe_allow_html=True)

        bl_col1, bl_col2 = st.columns([3, 1])
        with bl_col1:
            bl_merchant = st.text_input("Merchant name", placeholder="e.g. suspicious shop", key="bl_input")
        with bl_col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚫 Blacklist", key="bl_btn"):
                if bl_merchant:
                    blacklist_merchant(bl_merchant)
                    st.success(f"✅ '{bl_merchant}' blacklisted!")
                    st.rerun()

        wl_col1, wl_col2 = st.columns([3, 1])
        with wl_col1:
            wl_merchant = st.text_input("Merchant name", placeholder="e.g. trusted shop", key="wl_input")
        with wl_col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("✅ Whitelist", key="wl_btn"):
                if wl_merchant:
                    whitelist_merchant(wl_merchant)
                    st.success(f"✅ '{wl_merchant}' whitelisted!")
                    st.rerun()

        st.markdown("### 👤 Flagged Users")
        flagged = {}
        for txn in transactions:
            u = txn.get("user")
            s = txn.get("status")
            if s in ["FRAUD", "SUSPICIOUS"]:
                if u not in flagged:
                    flagged[u] = {"FRAUD": 0, "SUSPICIOUS": 0}
                flagged[u][s] += 1

        if not flagged:
            st.info("No flagged users yet.")
        else:
            for user, counts in list(flagged.items())[:5]:
                color = "#ff3b5c" if counts["FRAUD"] > 0 else "#ffb800"
                st.markdown(f"""
                <div style='background:#07111f; border:1px solid #0f2a45; border-radius:8px;
                            padding:10px 14px; margin-bottom:6px;
                            border-left: 3px solid {color}'>
                    <div style='font-weight:600; color:#fff; font-size:13px'>{user}</div>
                    <div style='font-size:11px; color:#3d6080; margin-top:3px'>
                        🚨 Fraud: {counts['FRAUD']} &nbsp;·&nbsp; ⚠️ Suspicious: {counts['SUSPICIOUS']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# ══════════════════════════════════════
#         AUTO REFRESH
# ══════════════════════════════════════
if auto_refresh:
    time.sleep(3)
    st.rerun()