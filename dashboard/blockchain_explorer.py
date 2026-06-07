import streamlit as st
import requests
import json
import hashlib
import time
import sys
import os
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


st.set_page_config(
    page_title="AntiFraud MUJ — Blockchain Explorer",
    page_icon="⛓️",
    layout="wide"
)

BASE_URL = "http://127.0.0.1:8000"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=Share+Tech+Mono&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background: #040b14 !important;
    color: #c8dff0 !important;
}

.stApp { background: #040b14 !important; }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
.block-container { padding: 2rem 3rem !important; }

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-thumb { background: #0f2a45; border-radius: 4px; }

/* ── HEADER ── */
.exp-header {
    margin-bottom: 32px;
    padding-bottom: 20px;
    border-bottom: 1px solid #0f2a45;
}

.exp-title {
    font-family: 'Syne', sans-serif;
    font-size: 28px;
    font-weight: 800;
    color: #fff;
    letter-spacing: -0.02em;
    margin-bottom: 4px;
}

.exp-title span { color: #00d4ff; }

.exp-sub {
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: #3d6080;
    letter-spacing: 0.12em;
}

/* ── CHAIN STATS ── */
.chain-stats {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 14px;
    margin-bottom: 28px;
}

.cstat {
    background: #07111f;
    border: 1px solid #0f2a45;
    border-radius: 12px;
    padding: 16px;
    position: relative;
    overflow: hidden;
}

.cstat::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #00d4ff, transparent);
}

.cstat-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    color: #3d6080;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 6px;
}

.cstat-value {
    font-family: 'Syne', sans-serif;
    font-size: 22px;
    font-weight: 800;
    color: #fff;
    line-height: 1;
}

/* ── BLOCK CARDS ── */
.block-card {
    background: #07111f;
    border: 1px solid #0f2a45;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 12px;
    transition: border-color 0.2s, transform 0.15s;
    cursor: pointer;
    position: relative;
    overflow: hidden;
}

.block-card:hover {
    border-color: rgba(0,212,255,0.4);
    transform: translateY(-1px);
}

.block-card.genesis { border-color: rgba(0,255,157,0.3); }
.block-card.fraud-block { border-color: rgba(255,59,92,0.3); }
.block-card.suspicious-block { border-color: rgba(255,184,0,0.3); }

.block-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 14px;
}

.block-num {
    font-family: 'Share Tech Mono', monospace;
    font-size: 13px;
    font-weight: 700;
    color: #00d4ff;
}

.block-time {
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    color: #3d6080;
}

.block-status {
    padding: 3px 10px;
    border-radius: 100px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    font-weight: 700;
}

.block-status.verified {
    background: rgba(0,255,157,0.08);
    color: #00ff9d;
    border: 1px solid rgba(0,255,157,0.25);
}

.hash-display {
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: #3d6080;
    margin-bottom: 6px;
    word-break: break-all;
    line-height: 1.6;
}

.hash-display span { color: #00d4ff; }
.hash-display .prev-hash { color: #6b82a8; }

.block-body {
    background: #0a1828;
    border-radius: 8px;
    padding: 12px 14px;
    margin-top: 10px;
}

.txn-detail {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 10px;
    margin-top: 8px;
}

.txn-detail-item {
    font-size: 12px;
}

.txn-detail-label {
    color: #3d6080;
    font-size: 10px;
    font-family: 'Share Tech Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 2px;
}

.txn-detail-value {
    color: #c8dff0;
    font-weight: 500;
}

.risk-inline {
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

.risk-pill {
    padding: 2px 8px;
    border-radius: 100px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    font-weight: 700;
}

.risk-pill.fraud      { background: rgba(255,59,92,0.12); color: #ff3b5c; border: 1px solid rgba(255,59,92,0.3); }
.risk-pill.suspicious { background: rgba(255,184,0,0.10); color: #ffb800; border: 1px solid rgba(255,184,0,0.3); }
.risk-pill.safe       { background: rgba(0,230,118,0.08); color: #00e676; border: 1px solid rgba(0,230,118,0.25); }

.chain-link {
    text-align: center;
    color: #0f2a45;
    font-size: 20px;
    margin: -4px 0;
    font-family: 'Share Tech Mono', monospace;
}

/* ── TAMPER DEMO ── */
.tamper-wrap {
    background: #07111f;
    border: 1px solid #0f2a45;
    border-radius: 14px;
    padding: 24px;
    margin-bottom: 20px;
}

.tamper-title {
    font-family: 'Syne', sans-serif;
    font-size: 17px;
    font-weight: 700;
    color: #fff;
    margin-bottom: 6px;
}

.tamper-sub {
    font-size: 13px;
    color: #3d6080;
    margin-bottom: 20px;
    line-height: 1.6;
}

.hash-compare {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
    margin-top: 16px;
}

.hash-box {
    background: #0a1828;
    border-radius: 10px;
    padding: 14px;
    border: 1px solid #0f2a45;
}

.hash-box-label {
    font-family: 'Share Tech Mono', monospace;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 8px;
}

.hash-box-label.original { color: #00e676; }
.hash-box-label.tampered { color: #ff3b5c; }

.hash-value {
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    word-break: break-all;
    line-height: 1.7;
}

.hash-value.original { color: #00e676; }
.hash-value.tampered { color: #ff3b5c; }

.mismatch-banner {
    background: rgba(255,59,92,0.08);
    border: 1px solid rgba(255,59,92,0.3);
    border-radius: 10px;
    padding: 14px 18px;
    margin-top: 14px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 12px;
    color: #ff3b5c;
    text-align: center;
    animation: flash 1.5s infinite;
}

.match-banner {
    background: rgba(0,230,118,0.08);
    border: 1px solid rgba(0,230,118,0.3);
    border-radius: 10px;
    padding: 14px 18px;
    margin-top: 14px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 12px;
    color: #00e676;
    text-align: center;
}

@keyframes flash {
    0%,100% { opacity: 1; }
    50% { opacity: 0.6; }
}

/* ── AUDIT ── */
.audit-wrap {
    background: #07111f;
    border: 1px solid #0f2a45;
    border-radius: 14px;
    padding: 24px;
}

.audit-result {
    background: #0a1828;
    border-radius: 10px;
    padding: 16px;
    margin-top: 16px;
    font-family: 'Share Tech Mono', monospace;
    font-size: 12px;
    color: #6b82a8;
    line-height: 2;
}

.audit-result .highlight { color: #00d4ff; }
.audit-result .safe-text { color: #00e676; }
.audit-result .danger-text { color: #ff3b5c; }

/* ── INPUTS ── */
.stTextInput > div > div > input {
    background: #0a1828 !important;
    border: 1px solid #0f2a45 !important;
    border-radius: 8px !important;
    color: #c8dff0 !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 13px !important;
}

.stTextInput > div > div > input:focus {
    border-color: #00d4ff !important;
}

.stSelectbox > div > div {
    background: #0a1828 !important;
    border: 1px solid #0f2a45 !important;
    border-radius: 8px !important;
    color: #c8dff0 !important;
}

label {
    color: #6b82a8 !important;
    font-size: 12px !important;
    font-family: 'Share Tech Mono', monospace !important;
}

.stButton > button {
    background: #07111f !important;
    border: 1px solid #0f2a45 !important;
    color: #00d4ff !important;
    border-radius: 8px !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 12px !important;
    letter-spacing: 0.05em !important;
    transition: all 0.2s !important;
}

.stButton > button:hover {
    border-color: #00d4ff !important;
    background: rgba(0,212,255,0.06) !important;
}

hr { border-color: #0f2a45 !important; }

div[data-testid="column"] { padding: 0 8px !important; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════
#         LOAD DATA
# ══════════════════════════════════════
@st.cache_data(ttl=3)
def load_chain():
    try:
        r = requests.get(f"{BASE_URL}/blockchain/chain", timeout=5)
        return r.json()
    except:
        return {"chain": [], "length": 0}

@st.cache_data(ttl=3)
def validate_chain():
    try:
        r = requests.get(f"{BASE_URL}/blockchain/validate", timeout=5)
        return r.json()
    except:
        return {"valid": False, "blocks": 0}

def compute_hash(block_data: dict) -> str:
    import json
    return hashlib.sha256(
        json.dumps(block_data, sort_keys=True).encode()
    ).hexdigest()

# ══════════════════════════════════════
#         HEADER
# ══════════════════════════════════════
st.markdown("""
<div class='exp-header'>
    <div class='exp-title'>⛓️ Vault<span>Sense</span> — Blockchain Explorer</div>
    <div class='exp-sub'>// IMMUTABLE TRANSACTION LEDGER · SHA-256 PROOF OF WORK · TAMPER DETECTION</div>
</div>
""", unsafe_allow_html=True)

chain_data = load_chain()
valid_data = validate_chain()
chain      = chain_data.get("chain", [])

# ══════════════════════════════════════
#         CHAIN STATS
# ══════════════════════════════════════
total_blocks = len(chain)
txn_blocks   = [b for b in chain if b["index"] > 0]
all_txns     = []
for b in txn_blocks:
    for t in b.get("transactions", []):
        if isinstance(t, dict) and "tx_id" in t:
            all_txns.append(t)

fraud_blocks = sum(1 for t in all_txns if t.get("status") == "FRAUD")
susp_blocks  = sum(1 for t in all_txns if t.get("status") == "SUSPICIOUS")
safe_blocks  = sum(1 for t in all_txns if t.get("status") == "SAFE")
total_value  = sum(t.get("amount", 0) for t in all_txns)
chain_ok     = valid_data.get("valid", False)

st.markdown(f"""
<div class='chain-stats'>
    <div class='cstat'>
        <div class='cstat-label'>Total Blocks</div>
        <div class='cstat-value'>{total_blocks}</div>
    </div>
    <div class='cstat'>
        <div class='cstat-label'>Transactions</div>
        <div class='cstat-value'>{len(all_txns)}</div>
    </div>
    <div class='cstat'>
        <div class='cstat-label'>Value Secured</div>
        <div class='cstat-value' style='font-size:16px'>₹{total_value:,.0f}</div>
    </div>
    <div class='cstat'>
        <div class='cstat-label'>Fraud Caught</div>
        <div class='cstat-value' style='color:#ff3b5c'>{fraud_blocks}</div>
    </div>
    <div class='cstat'>
        <div class='cstat-label'>Chain Integrity</div>
        <div class='cstat-value' style='color:{"#00e676" if chain_ok else "#ff3b5c"}; font-size:16px'>
            {"INTACT ✓" if chain_ok else "BROKEN ✗"}
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════
#         TABS
# ══════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "⛓️ Block Explorer",
    "🔬 Tamper Detection Demo",
    "📋 Audit & Verify",
    "🕸️ Fraud Network Graph"
])

# ════════════════════════════════
#   TAB 1 — BLOCK EXPLORER
# ════════════════════════════════
with tab1:
    if st.button("🔄 Refresh Chain"):
        st.cache_data.clear()
        st.rerun()

    if not chain:
        st.info("No blocks yet. Start making transactions from the banking app!")
    else:
        st.markdown(f"<br>", unsafe_allow_html=True)
        for i, block in enumerate(reversed(chain)):
            txns     = block.get("transactions", [])
            is_gen   = block["index"] == 0
            card_cls = "genesis" if is_gen else ""

            # Determine block type from transactions
            statuses = [t.get("status","") for t in txns if isinstance(t,dict)]
            if "FRAUD" in statuses:
                card_cls = "fraud-block"
            elif "SUSPICIOUS" in statuses:
                card_cls = "suspicious-block"

            with st.expander(
                f"{'🟢 GENESIS' if is_gen else '🔷 Block'} #{block['index']} "
                f"· {block['timestamp']} "
                f"· {len(txns)} txn{'s' if len(txns)!=1 else ''}",
                expanded=(i == 0)
            ):
                st.markdown(f"""
                <div class='block-card {card_cls}'>
                    <div class='block-header'>
                        <div class='block-num'>BLOCK #{block['index']}</div>
                        <div style='display:flex; gap:8px; align-items:center'>
                            <div class='block-time'>{block['timestamp']}</div>
                            <div class='block-status verified'>✓ VERIFIED</div>
                        </div>
                    </div>
                    <div class='hash-display'>
                        Hash: <span>{block['hash']}</span>
                    </div>
                    <div class='hash-display'>
                        Prev: <span class='prev-hash'>{block['previous_hash']}</span>
                    </div>
                    <div class='hash-display'>
                        Nonce: <span>{block['nonce']}</span>
                        &nbsp;·&nbsp; Transactions: <span>{len(txns)}</span>
                    </div>
                """, unsafe_allow_html=True)

                # Transaction details
                for txn in txns:
                    if not isinstance(txn, dict) or "tx_id" not in txn:
                        continue
                    s   = txn.get("status","SAFE")
                    sc  = {"FRAUD":"fraud","SUSPICIOUS":"suspicious","SAFE":"safe"}.get(s,"safe")
                    amt = txn.get("amount", 0)

                    st.markdown(f"""
                    <div class='block-body'>
                        <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:8px'>
                            <div style='font-family:Share Tech Mono,monospace; font-size:12px; color:#00d4ff'>
                                {txn.get('tx_id','N/A')}
                            </div>
                            <div class='risk-pill {sc}'>{s}</div>
                        </div>
                        <div class='txn-detail'>
                            <div class='txn-detail-item'>
                                <div class='txn-detail-label'>User</div>
                                <div class='txn-detail-value'>{txn.get('user_id','N/A')}</div>
                            </div>
                            <div class='txn-detail-item'>
                                <div class='txn-detail-label'>Merchant</div>
                                <div class='txn-detail-value'>{txn.get('merchant','N/A')}</div>
                            </div>
                            <div class='txn-detail-item'>
                                <div class='txn-detail-label'>Amount</div>
                                <div class='txn-detail-value'>₹{amt:,.2f}</div>
                            </div>
                            <div class='txn-detail-item'>
                                <div class='txn-detail-label'>Category</div>
                                <div class='txn-detail-value'>{txn.get('merchant_category','N/A')}</div>
                            </div>
                            <div class='txn-detail-item'>
                                <div class='txn-detail-label'>Risk Score</div>
                                <div class='txn-detail-value' style='color:{"#ff3b5c" if txn.get("risk_score",0)>=65 else "#ffb800" if txn.get("risk_score",0)>=35 else "#00e676"}'>
                                    {txn.get('risk_score',0):.1f}/100
                                </div>
                            </div>
                            <div class='txn-detail-item'>
                                <div class='txn-detail-label'>Timestamp</div>
                                <div class='txn-detail-value'>{txn.get('timestamp','N/A')}</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)

            # Chain connector
            if i < len(chain) - 1:
                st.markdown("<div class='chain-link'>│<br/>└──▶</div>", unsafe_allow_html=True)

# ════════════════════════════════
#   TAB 2 — TAMPER DETECTION
# ════════════════════════════════
with tab2:
    st.markdown("""
    <div style='margin-bottom:20px'>
        <div style='font-family:Syne,sans-serif; font-size:20px; font-weight:700; color:#fff; margin-bottom:6px'>
            🔬 Tamper Detection Demo
        </div>
        <div style='font-size:13px; color:#3d6080; line-height:1.7'>
            Select a transaction, modify any value, then click <b style='color:#00d4ff'>Run Tamper Test</b>.
            The blockchain will instantly detect the change through hash mismatch —
            proving records are cryptographically immutable.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not all_txns:
        st.info("Make some transactions first, then come back here to test tamper detection!")
    else:
        txn_ids  = [t.get("tx_id","") for t in all_txns if t.get("tx_id")]
        selected = st.selectbox("Select a Transaction to Tamper With", txn_ids)
        sel_txn  = next((t for t in all_txns if t.get("tx_id") == selected), None)

        if sel_txn:
            sel_block = None
            for b in chain:
                for t in b.get("transactions", []):
                    if isinstance(t, dict) and t.get("tx_id") == selected:
                        sel_block = b
                        break

            if sel_block:
                st.markdown(f"""
                <div style='background:#0a1828; border:1px solid #0f2a45; border-radius:10px;
                            padding:14px 18px; margin:16px 0; font-family:Share Tech Mono,monospace;
                            font-size:11px; color:#6b82a8'>
                    📦 Block #{sel_block['index']} &nbsp;·&nbsp;
                    Original Hash: <span style='color:#00d4ff'>{sel_block['hash']}</span>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("**Step 1 — Modify the transaction data below:**")
                c1, c2 = st.columns(2)
                with c1:
                    new_amount   = st.number_input("Amount (₹)", value=float(sel_txn.get("amount", 100)), key="tamp_amt")
                    new_merchant = st.text_input("Merchant",     value=sel_txn.get("merchant", ""),       key="tamp_mer")
                with c2:
                    new_status = st.selectbox("Status",
                                              ["SAFE", "SUSPICIOUS", "FRAUD"],
                                              index=["SAFE","SUSPICIOUS","FRAUD"].index(sel_txn.get("status","SAFE")),
                                              key="tamp_sta")
                    new_score  = st.number_input("Risk Score", value=float(sel_txn.get("risk_score", 0)), key="tamp_sco")

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("**Step 2 — Run the tamper test:**")

                if st.button("🔨 Run Tamper Test", key="tamper_btn"):
                    with st.spinner("🔍 Computing hashes and verifying chain integrity..."):
                        time.sleep(1.5)

                    original_block_data = {
                        "index"        : sel_block["index"],
                        "timestamp"    : sel_block["timestamp"],
                        "transactions" : sel_block["transactions"],
                        "previous_hash": sel_block["previous_hash"],
                        "nonce"        : sel_block["nonce"]
                    }
                    original_hash = compute_hash(original_block_data)

                    tampered_txn = {**sel_txn,
                        "amount"    : new_amount,
                        "merchant"  : new_merchant,
                        "status"    : new_status,
                        "risk_score": new_score
                    }
                    tampered_transactions = []
                    for t in sel_block["transactions"]:
                        if isinstance(t, dict) and t.get("tx_id") == selected:
                            tampered_transactions.append(tampered_txn)
                        else:
                            tampered_transactions.append(t)

                    tampered_block_data = {
                        "index"        : sel_block["index"],
                        "timestamp"    : sel_block["timestamp"],
                        "transactions" : tampered_transactions,
                        "previous_hash": sel_block["previous_hash"],
                        "nonce"        : sel_block["nonce"]
                    }
                    tampered_hash = compute_hash(tampered_block_data)
                    is_tampered   = original_hash != tampered_hash

                    # Step by step reveal
                    st.markdown("**Step 3 — Results:**")
                    st.markdown(f"""
                    <div class='hash-compare'>
                        <div class='hash-box'>
                            <div class='hash-box-label original'>✓ ORIGINAL HASH</div>
                            <div class='hash-value original'>{original_hash}</div>
                        </div>
                        <div class='hash-box'>
                            <div class='hash-box-label {"tampered" if is_tampered else "original"}'>
                                {"⚠ TAMPERED HASH — MISMATCH DETECTED" if is_tampered else "✓ UNCHANGED HASH"}
                            </div>
                            <div class='hash-value {"tampered" if is_tampered else "original"}'>{tampered_hash}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    if is_tampered:
                        # Show what changed
                        changes = []
                        if new_amount   != sel_txn.get("amount"):    changes.append(f"Amount: ₹{sel_txn.get('amount')} → ₹{new_amount}")
                        if new_merchant != sel_txn.get("merchant"):  changes.append(f"Merchant: {sel_txn.get('merchant')} → {new_merchant}")
                        if new_status   != sel_txn.get("status"):    changes.append(f"Status: {sel_txn.get('status')} → {new_status}")
                        if new_score    != sel_txn.get("risk_score"): changes.append(f"Risk Score: {sel_txn.get('risk_score')} → {new_score}")

                        changes_html = "".join([f"<div>⚡ {c}</div>" for c in changes])
                        st.markdown(f"""
                        <div class='mismatch-banner'>
                            🚨 TAMPER DETECTED — Blockchain integrity compromised!<br/><br/>
                            <div style='font-size:11px; text-align:left; margin-top:8px; color:#ffb800'>
                                CHANGES DETECTED:<br/>{changes_html}
                            </div><br/>
                            The original record is permanently preserved on the chain.
                            Any attempt to alter it is immediately detected and flagged.
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                        <div class='match-banner'>
                            ✓ No tampering detected — Hashes match perfectly.
                            Change any value above and re-run to see tamper detection in action.
                        </div>
                        """, unsafe_allow_html=True)

# ════════════════════════════════
#   TAB 3 — AUDIT & VERIFY
# ════════════════════════════════
with tab3:
    st.markdown("""
    <div style='margin-bottom:20px'>
        <div style='font-family:Syne,sans-serif; font-size:20px; font-weight:700;
                    color:#fff; margin-bottom:6px'>
            📋 Transaction Audit
        </div>
        <div style='font-size:13px; color:#3d6080; line-height:1.7'>
            Enter any Transaction ID to pull its complete immutable audit record
            from the blockchain. This proves the transaction existed, when it
            occurred, and that it has not been altered since recording.
        </div>
    </div>
    """, unsafe_allow_html=True)

    tx_input = st.text_input("Enter Transaction ID", placeholder="e.g. TXN-01001", key="audit_tx")

    if st.button("🔍 Run Audit", key="audit_btn"):
        if not tx_input:
            st.error("Please enter a Transaction ID.")
        else:
            found_txn   = None
            found_block = None
            for b in chain:
                for t in b.get("transactions",[]):
                    if isinstance(t,dict) and t.get("tx_id","").upper() == tx_input.upper():
                        found_txn   = t
                        found_block = b
                        break

            if not found_txn:
                st.error(f"Transaction `{tx_input}` not found in blockchain.")
            else:
                s      = found_txn.get("status","SAFE")
                sc     = {"FRAUD":"danger-text","SUSPICIOUS":"highlight","SAFE":"safe-text"}.get(s,"safe-text")
                amt    = found_txn.get("amount",0)
                score  = found_txn.get("risk_score",0)

                # Verify hash
                block_data_check = {
                    "index"        : found_block["index"],
                    "timestamp"    : found_block["timestamp"],
                    "transactions" : found_block["transactions"],
                    "previous_hash": found_block["previous_hash"],
                    "nonce"        : found_block["nonce"]
                }
                recomputed = compute_hash(block_data_check)
                integrity  = recomputed == found_block["hash"]

                st.markdown(f"""
                <div class='audit-result'>
╔══════════════════════════════════════════════════════════╗<br/>
║           VAULTSENSE — BLOCKCHAIN AUDIT REPORT           ║<br/>
╚══════════════════════════════════════════════════════════╝<br/>
<br/>
AUDIT TIMESTAMP &nbsp;&nbsp;: <span class='highlight'>{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</span><br/>
TRANSACTION ID &nbsp;&nbsp;&nbsp;: <span class='highlight'>{found_txn.get('tx_id','N/A')}</span><br/>
BLOCK NUMBER &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: <span class='highlight'>#{found_block['index']}</span><br/>
BLOCK TIMESTAMP &nbsp;&nbsp;: <span class='highlight'>{found_block['timestamp']}</span><br/>
<br/>
── TRANSACTION DETAILS ────────────────────────────────────<br/>
USER &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: <span class='highlight'>{found_txn.get('user_id','N/A')}</span><br/>
MERCHANT &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: <span class='highlight'>{found_txn.get('merchant','N/A')}</span><br/>
CATEGORY &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: <span class='highlight'>{found_txn.get('merchant_category','N/A')}</span><br/>
AMOUNT &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: <span class='highlight'>₹{amt:,.2f}</span><br/>
HOUR &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: <span class='highlight'>{found_txn.get('hour','N/A')}:00</span><br/>
<br/>
── AI RISK ASSESSMENT ─────────────────────────────────────<br/>
RISK SCORE &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: <span class='{sc}'>{score:.2f}/100</span><br/>
STATUS &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: <span class='{sc}'>{s}</span><br/>
<br/>
── BLOCKCHAIN VERIFICATION ────────────────────────────────<br/>
BLOCK HASH &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: <span class='highlight'>{found_block['hash'][:32]}...</span><br/>
PREV HASH &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: <span class='highlight'>{found_block['previous_hash'][:32]}...</span><br/>
NONCE &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;: <span class='highlight'>{found_block['nonce']}</span><br/>
HASH RECOMPUTED &nbsp;&nbsp;: <span class='highlight'>{recomputed[:32]}...</span><br/>
INTEGRITY CHECK &nbsp;&nbsp;: <span class='{"safe-text" if integrity else "danger-text"}'>
{"✓ VERIFIED — Record is authentic and untampered" if integrity else "✗ FAILED — Record integrity compromised!"}</span><br/>
<br/>
── CONCLUSION ─────────────────────────────────────────────<br/>
<span class='{"safe-text" if integrity else "danger-text"}'>
{"This transaction record is cryptographically verified." if integrity else "WARNING: This record may have been tampered with."}<br/>
{"It has not been altered since being recorded on the blockchain." if integrity else "Immediate investigation recommended."}
</span><br/>
<br/>
Generated by VaultSense Blockchain Audit System v1.0<br/>
</div>
                """, unsafe_allow_html=True)
# ════════════════════════════════
#   TAB 4 — FRAUD NETWORK GRAPH
# ════════════════════════════════
with tab4:
    st.markdown("""
    <div style='margin-bottom:20px'>
        <div style='font-family:Syne,sans-serif; font-size:20px; font-weight:700; color:#fff; margin-bottom:6px'>
            🕸️ Transaction Network Graph
        </div>
        <div style='font-size:13px; color:#3d6080; line-height:1.7'>
            Visual network of users and merchants. Red nodes = fraud, yellow = suspicious.
            Clusters reveal potential fraud rings — multiple users hitting the same suspicious merchant.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not all_txns:
        st.info("No transactions yet to visualize.")
    else:
        # Build network data
        nodes_users     = {}
        nodes_merchants = {}
        edges           = []

        for txn in all_txns:
            user     = txn.get("user_id", "Unknown")
            merchant = txn.get("merchant", "Unknown")
            status   = txn.get("status", "SAFE")
            amount   = txn.get("amount", 0)
            score    = txn.get("risk_score", 0)

            # User node
            if user not in nodes_users:
                nodes_users[user] = {"fraud": 0, "suspicious": 0, "safe": 0, "total": 0}
            nodes_users[user]["total"] += 1
            nodes_users[user][status.lower()] += 1

            # Merchant node
            if merchant not in nodes_merchants:
                nodes_merchants[merchant] = {"fraud": 0, "suspicious": 0, "safe": 0, "total": 0}
            nodes_merchants[merchant]["total"] += 1
            nodes_merchants[merchant][status.lower()] += 1

            edges.append((user, merchant, status, amount, score))

        # Layout — simple circular for users, merchants in center
        import math
        node_x, node_y, node_text, node_color, node_size, node_symbol = [], [], [], [], [], []

        # Place users in a circle
        user_list = list(nodes_users.keys())
        for i, user in enumerate(user_list):
            angle = 2 * math.pi * i / max(len(user_list), 1)
            x     = math.cos(angle) * 3
            y     = math.sin(angle) * 3
            node_x.append(x)
            node_y.append(y)
            node_text.append(f"👤 {user}<br>Txns: {nodes_users[user]['total']}<br>Fraud: {nodes_users[user]['fraud']}")

            if nodes_users[user]["fraud"] > 0:
                node_color.append("#ff3b5c")
            elif nodes_users[user]["suspicious"] > 0:
                node_color.append("#ffb800")
            else:
                node_color.append("#00d4ff")

            node_size.append(20 + nodes_users[user]["total"] * 3)
            node_symbol.append("circle")

        # Place merchants in inner circle
        merch_list = list(nodes_merchants.keys())
        merch_positions = {}
        for i, merchant in enumerate(merch_list):
            angle = 2 * math.pi * i / max(len(merch_list), 1)
            x     = math.cos(angle) * 1.2
            y     = math.sin(angle) * 1.2
            merch_positions[merchant] = (x, y)
            node_x.append(x)
            node_y.append(y)
            node_text.append(f"🏪 {merchant}<br>Txns: {nodes_merchants[merchant]['total']}<br>Fraud: {nodes_merchants[merchant]['fraud']}")

            if nodes_merchants[merchant]["fraud"] > 0:
                node_color.append("#ff3b5c")
            elif nodes_merchants[merchant]["suspicious"] > 0:
                node_color.append("#ffb800")
            else:
                node_color.append("#00e676")

            node_size.append(15 + nodes_merchants[merchant]["total"] * 2)
            node_symbol.append("diamond")

        # Build edge traces
        edge_traces = []
        user_positions = {
            user: (
                math.cos(2 * math.pi * i / max(len(user_list), 1)) * 3,
                math.sin(2 * math.pi * i / max(len(user_list), 1)) * 3
            )
            for i, user in enumerate(user_list)
        }

        for user, merchant, status, amount, score in edges:
            if user in user_positions and merchant in merch_positions:
                ux, uy = user_positions[user]
                mx, my = merch_positions[merchant]
                color  = {"FRAUD": "rgba(255,59,92,0.4)",
                          "SUSPICIOUS": "rgba(255,184,0,0.3)",
                          "SAFE": "rgba(0,212,255,0.15)"}.get(status, "rgba(0,212,255,0.15)")
                edge_traces.append(go.Scatter(
                    x=[ux, mx, None], y=[uy, my, None],
                    mode="lines",
                    line=dict(width=1.5, color=color),
                    hoverinfo="none",
                    showlegend=False
                ))

        # Node trace
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode="markers",
            hoverinfo="text",
            text=node_text,
            marker=dict(
                color=node_color,
                size=node_size,
                symbol=node_symbol,
                line=dict(width=1, color="#0f2a45")
            ),
            showlegend=False
        )

        fig = go.Figure(
            data=edge_traces + [node_trace],
            layout=go.Layout(
                paper_bgcolor="#040b14",
                plot_bgcolor="#040b14",
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                margin=dict(t=20, b=20, l=20, r=20),
                height=550,
                hovermode="closest"
            )
        )
        st.plotly_chart(fig, use_container_width=True)

        # Legend
        st.markdown("""
        <div style='display:flex; gap:24px; font-family:Share Tech Mono,monospace; font-size:11px; margin-top:8px'>
            <span><span style='color:#ff3b5c'>●</span> Fraud</span>
            <span><span style='color:#ffb800'>●</span> Suspicious</span>
            <span><span style='color:#00d4ff'>●</span> Safe User</span>
            <span><span style='color:#00e676'>◆</span> Safe Merchant</span>
            <span style='color:#3d6080'>Circle = User · Diamond = Merchant</span>
        </div>
        """, unsafe_allow_html=True)

        # Fraud ring detection
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**🔍 Fraud Ring Detection**")
        fraud_merchants = [m for m, d in nodes_merchants.items() if d["fraud"] > 0]
        rings_found = False
        for merchant in fraud_merchants:
            users_hitting = list(set(
                e[0] for e in edges
                if e[1] == merchant and e[2] == "FRAUD"
            ))
            if len(users_hitting) >= 2:
                rings_found = True
                st.markdown(f"""
                <div style='background:rgba(255,59,92,0.08); border:1px solid rgba(255,59,92,0.3);
                            border-radius:10px; padding:14px 18px; margin-bottom:8px;
                            font-family:Share Tech Mono,monospace; font-size:12px'>
                    🚨 FRAUD RING DETECTED — Merchant: <span style='color:#ff3b5c'>{merchant}</span><br/>
                    <span style='color:#ffb800'>Users involved: {", ".join(users_hitting)}</span>
                </div>
                """, unsafe_allow_html=True)

        if not rings_found:
            st.info("No fraud rings detected yet. Run the demo simulation to generate fraud patterns.")
# ── AUTO REFRESH ──
if st.button("🔄 Refresh Data", key="refresh_all"):
    st.cache_data.clear()
    st.rerun()

st.markdown(f"""
<div style='text-align:center; padding:20px 0; font-family:Share Tech Mono,monospace;
            font-size:10px; color:#1e3a5f; letter-spacing:0.1em'>
    VAULTSENSE BLOCKCHAIN EXPLORER v1.0 &nbsp;·&nbsp;
    SHA-256 PROOF OF WORK &nbsp;·&nbsp;
    {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
</div>
""", unsafe_allow_html=True)