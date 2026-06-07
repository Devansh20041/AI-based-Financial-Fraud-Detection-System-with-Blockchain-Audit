import requests
import time
import os
import sys
from datetime import datetime

# ── Colors ──
class C:
    RED     = '\033[91m'
    GREEN   = '\033[92m'
    YELLOW  = '\033[93m'
    BLUE    = '\033[94m'
    CYAN    = '\033[96m'
    WHITE   = '\033[97m'
    BOLD    = '\033[1m'
    DIM     = '\033[2m'
    RESET   = '\033[0m'

BASE_URL = "http://127.0.0.1:8000"

def clear(): os.system('cls' if os.name == 'nt' else 'clear')

def typewrite(text, delay=0.018):
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def divider(char="─", width=65, color=C.DIM):
    print(f"{color}{char * width}{C.RESET}")

def header():
    clear()
    print(f"\n{C.CYAN}{C.BOLD}")
    print("  ███████╗██╗███╗   ██╗ ██████╗ ██╗   ██╗ █████╗ ██████╗ ██████╗ ")
    print("  ██╔════╝██║████╗  ██║██╔════╝ ██║   ██║██╔══██╗██╔══██╗██╔══██╗")
    print("  █████╗  ██║██╔██╗ ██║██║  ███╗██║   ██║███████║██████╔╝██║  ██║")
    print("  ██╔══╝  ██║██║╚██╗██║██║   ██║██║   ██║██╔══██║██╔══██╗██║  ██║")
    print("  ██║     ██║██║ ╚████║╚██████╔╝╚██████╔╝██║  ██║██║  ██║██████╔╝")
    print("  ╚═╝     ╚═╝╚═╝  ╚═══╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ")
    print(f"{C.RESET}")
    print(f"  {C.DIM}Secure Financial Monitoring System · v1.0.0{C.RESET}")
    print(f"  {C.DIM}Hybrid ML · Blockchain Verification · Behavioral Profiling{C.RESET}")
    divider("═", 65, C.CYAN)

def status_badge(status):
    if status == "FRAUD":
        return f"{C.RED}{C.BOLD}  🚨 FRAUD      {C.RESET}"
    elif status == "SUSPICIOUS":
        return f"{C.YELLOW}{C.BOLD}  ⚠️  SUSPICIOUS {C.RESET}"
    else:
        return f"{C.GREEN}{C.BOLD}  ✅ SAFE        {C.RESET}"

def risk_bar(score, width=20):
    filled = int((score / 100) * width)
    empty  = width - filled
    if score >= 65:
        color = C.RED
    elif score >= 35:
        color = C.YELLOW
    else:
        color = C.GREEN
    bar = f"{color}{'█' * filled}{C.DIM}{'░' * empty}{C.RESET}"
    return f"{bar} {color}{C.BOLD}{score:>5.1f}/100{C.RESET}"

def analyze(txn):
    try:
        r = requests.post(f"{BASE_URL}/analyze", json=txn, timeout=10)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

def print_result(txn, result, index):
    print(f"\n  {C.CYAN}{C.BOLD}Transaction #{index:02d}{C.RESET}")
    divider("·", 65)
    print(f"  {C.DIM}TX ID      :{C.RESET} {C.WHITE}{result.get('tx_id','N/A')}{C.RESET}")
    print(f"  {C.DIM}User       :{C.RESET} {C.WHITE}{txn['user_id']}{C.RESET}")
    print(f"  {C.DIM}Merchant   :{C.RESET} {C.WHITE}{txn['merchant']}{C.RESET}")
    print(f"  {C.DIM}Category   :{C.RESET} {C.WHITE}{txn['merchant_category']}{C.RESET}")
    print(f"  {C.DIM}Amount     :{C.RESET} {C.WHITE}₹{txn['amount']:,.2f}{C.RESET}")
    print(f"  {C.DIM}Hour       :{C.RESET} {C.WHITE}{txn['hour']:02d}:00{C.RESET}")
    print(f"  {C.DIM}Risk Score :{C.RESET} {risk_bar(result.get('risk_score', 0))}")
    print(f"  {C.DIM}Status     :{C.RESET} {status_badge(result.get('status','N/A'))}")
    print(f"  {C.DIM}Block Hash :{C.RESET} {C.CYAN}{result.get('block_hash','N/A')[:20]}...{C.RESET}")
    print(f"  {C.DIM}Block #    :{C.RESET} {C.WHITE}{result.get('block_index','N/A')}{C.RESET}")
    print(f"  {C.DIM}Timestamp  :{C.RESET} {C.WHITE}{result.get('timestamp','N/A')}{C.RESET}")
    divider("·", 65)

# ── Test Transactions ──
transactions = [
    {
        "user_id": "USR-0042",
        "amount": 9999.00,
        "merchant": "Unknown Offshore Ltd.",
        "merchant_category": "Wire Transfer",
        "hour": 3,
        "V1": -3.04, "V2": -3.15, "V3": -2.27, "V14": -8.5
    },
    {
        "user_id": "USR-0071",
        "amount": 42.50,
        "merchant": "Starbucks",
        "merchant_category": "Food & Beverage",
        "hour": 9,
    },
    {
        "user_id": "USR-0118",
        "amount": 4200.00,
        "merchant": "Crypto Exchange Pro",
        "merchant_category": "Crypto Exchange",
        "hour": 2,
        "V4": 4.5, "V11": 3.2, "V14": -6.1
    },
    {
        "user_id": "USR-0305",
        "amount": 0.50,
        "merchant": "Unknown Merchant",
        "merchant_category": "ATM Withdrawal",
        "hour": 23,
        "V1": -2.1, "V3": -3.5
    },
    {
        "user_id": "USR-0014",
        "amount": 128.99,
        "merchant": "Amazon",
        "merchant_category": "E-Commerce",
        "hour": 14,
    },
    {
        "user_id": "USR-0200",
        "amount": 5500.00,
        "merchant": "Offshore Wire Services",
        "merchant_category": "Wire Transfer",
        "hour": 4,
        "V1": -4.2, "V2": -2.8, "V14": -9.1, "V17": -5.3
    },
    {
        "user_id": "USR-0099",
        "amount": 18.00,
        "merchant": "Netflix",
        "merchant_category": "Entertainment",
        "hour": 20,
    },
    {
        "user_id": "USR-0150",
        "amount": 1850.00,
        "merchant": "International Wire",
        "merchant_category": "Wire Transfer",
        "hour": 1,
        "V3": -2.9, "V10": -3.1
    },
]

# ── MAIN DEMO ──
if __name__ == "__main__":
    # Enable color on Windows
    os.system('color')

    header()

    # Check API
    typewrite(f"\n  {C.CYAN}[SYS]{C.RESET} Connecting to VaultSense API...", 0.02)
    try:
        r = requests.get(BASE_URL, timeout=5)
        typewrite(f"  {C.GREEN}[OK]{C.RESET}  API is ONLINE ✅", 0.02)
    except:
        typewrite(f"  {C.RED}[ERR]{C.RESET} API is OFFLINE. Start with: python main.py", 0.02)
        sys.exit(1)

    # Check blockchain
    typewrite(f"  {C.CYAN}[SYS]{C.RESET} Verifying blockchain integrity...", 0.02)
    r = requests.get(f"{BASE_URL}/blockchain/validate", timeout=5).json()
    if r.get('valid'):
        typewrite(f"  {C.GREEN}[OK]{C.RESET}  Blockchain VERIFIED ✅ ({r.get('blocks')} blocks)", 0.02)
    else:
        typewrite(f"  {C.RED}[WARN]{C.RESET} Blockchain integrity check failed!", 0.02)

    # Stats
    typewrite(f"  {C.CYAN}[SYS]{C.RESET} Loading system stats...", 0.02)
    stats = requests.get(f"{BASE_URL}/stats", timeout=5).json()
    typewrite(f"  {C.GREEN}[OK]{C.RESET}  {stats['total_users']} user profiles · Models: {', '.join(stats['models_loaded'])}", 0.015)

    divider("═", 65, C.CYAN)
    print(f"\n  {C.BOLD}{C.WHITE}⚡ LIVE TRANSACTION ANALYSIS DEMO{C.RESET}")
    print(f"  {C.DIM}Processing {len(transactions)} transactions in real-time...{C.RESET}\n")
    time.sleep(1)

    fraud_count = 0
    suspicious_count = 0
    safe_count = 0

    for i, txn in enumerate(transactions, 1):
        typewrite(f"  {C.DIM}[{datetime.now().strftime('%H:%M:%S')}] Analyzing transaction {i}/{len(transactions)}...{C.RESET}", 0.01)
        result = analyze(txn)

        if "error" in result:
            print(f"  {C.RED}Error: {result['error']}{C.RESET}")
            continue

        print_result(txn, result, i)

        status = result.get('status', '')
        if status == 'FRAUD': fraud_count += 1
        elif status == 'SUSPICIOUS': suspicious_count += 1
        else: safe_count += 1

        time.sleep(0.8)

    # ── SUMMARY ──
    divider("═", 65, C.CYAN)
    print(f"\n  {C.BOLD}{C.WHITE}📊 SESSION SUMMARY{C.RESET}")
    divider("·", 65)
    print(f"  {C.DIM}Total Analyzed  :{C.RESET} {C.WHITE}{len(transactions)}{C.RESET}")
    print(f"  {C.RED}{C.BOLD}  🚨 Fraud         : {fraud_count}{C.RESET}")
    print(f"  {C.YELLOW}{C.BOLD}  ⚠️  Suspicious    : {suspicious_count}{C.RESET}")
    print(f"  {C.GREEN}{C.BOLD}  ✅ Safe           : {safe_count}{C.RESET}")

    # Final blockchain check
    chain = requests.get(f"{BASE_URL}/blockchain/chain").json()
    print(f"\n  {C.CYAN}⛓  Blockchain     :{C.RESET} {C.WHITE}{chain['length']} blocks · All transactions immutably recorded{C.RESET}")
    validate = requests.get(f"{BASE_URL}/blockchain/validate").json()
    integrity = f"{C.GREEN}INTACT ✅{C.RESET}" if validate['valid'] else f"{C.RED}COMPROMISED ❌{C.RESET}"
    print(f"  {C.CYAN}🔒 Chain Integrity:{C.RESET} {integrity}")
    divider("═", 65, C.CYAN)
    print(f"\n  {C.DIM}VaultSense v1.0.0 · {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{C.RESET}\n")
