import os
import sys
import time
import webbrowser
from datetime import datetime

# ── Colors ──
class C:
    RED    = '\033[91m'
    GREEN  = '\033[92m'
    YELLOW = '\033[93m'
    CYAN   = '\033[96m'
    WHITE  = '\033[97m'
    BOLD   = '\033[1m'
    DIM    = '\033[2m'
    RESET  = '\033[0m'

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def log(status, msg):
    icons = {
        "ok"  : f"{C.GREEN}  ✅{C.RESET}",
        "info": f"{C.CYAN}  ℹ️ {C.RESET}",
        "warn": f"{C.YELLOW}  ⚠️ {C.RESET}",
        "err" : f"{C.RED}  ❌{C.RESET}",
        "run" : f"{C.CYAN}  🚀{C.RESET}",
    }
    print(f"   {icons.get(status,'')} {msg}")

def divider():
    print(f"   {C.DIM}{'─'*55}{C.RESET}")

def wait_for_api():
    import requests
    log("info", "Waiting for API to be ready...")
    attempt = 0
    while True:
        attempt += 1
        try:
            r = requests.get("http://127.0.0.1:8000", timeout=2)
            if r.status_code == 200:
                return True
        except:
            pass
        print(f"   {C.DIM}   ... attempt {attempt}{C.RESET}", flush=True)
        time.sleep(2)

if __name__ == "__main__":
    clear()
    print(f"\n{C.CYAN}{C.BOLD}")
    print("   ╔═══════════════════════════════════════════════════════╗")
    print("   ║            VaultSense — Startup Launcher             ║")
    print("   ║   AI Fraud Detection · Blockchain · Secure Banking   ║")
    print("   ╚═══════════════════════════════════════════════════════╝")
    print(f"{C.RESET}")
    print(f"   {C.DIM}Manipal University Jaipur · Major Project · 2026{C.RESET}\n")
    print(f"   {C.BOLD}{C.WHITE}Starting VaultSense...{C.RESET}")
    print(f"   {C.DIM}{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{C.RESET}\n")
    divider()

    # ── Start API in its own terminal window ──
    log("run", "Starting FastAPI Backend in new window...")
    os.system('start cmd /k "cd /d %CD% && uvicorn api.main:app --port 8000 --reload"')

    # ── Wait until API is truly ready ──
    wait_for_api()
    log("ok", "API is READY → http://127.0.0.1:8000")
    divider()

    # ── Start Banking App in its own window ──
    log("run", "Starting Banking App in new window...")
    os.system('start cmd /k "cd /d %CD% && streamlit run dashboard/user_app.py --server.port 8501 --server.headless true"')
    time.sleep(4)
    log("ok", "Banking App → http://localhost:8501")
    divider()

    # ── Start Security Dashboard in its own window ──
    log("run", "Starting Security Dashboard in new window...")
    os.system('start cmd /k "cd /d %CD% && streamlit run dashboard/security_app.py --server.port 8502 --server.headless true"')
    time.sleep(4)
    log("ok", "Security Dashboard → http://localhost:8502")
    log("run", "Starting Blockchain Explorer (port 8503)...")
    os.system('start cmd /k "cd /d %CD% && streamlit run dashboard/blockchain_explorer.py --server.port 8503 --server.headless true"')
    time.sleep(4)
    log("ok", "Blockchain Explorer → http://localhost:8503")
    divider()

    # ── Open Browsers ──
    log("info", "Opening browsers...")
    webbrowser.open("http://localhost:8501")
    time.sleep(0.5)
    webbrowser.open("http://localhost:8502")
    time.sleep(0.5)
    webbrowser.open("http://localhost:8000/docs")
    webbrowser.open("http://localhost:8503")

    print()
    divider()
    print(f"\n   {C.BOLD}{C.GREEN}🎉 VaultSense is fully running!{C.RESET}\n")
    print(f"   {C.WHITE}🏦 Banking App     → {C.CYAN}http://localhost:8501{C.RESET}")
    print(f"   {C.WHITE}🛡️  Security Center → {C.CYAN}http://localhost:8502{C.RESET}")
    print(f"   {C.WHITE}⛓️  Blockchain Explorer → {C.CYAN}http://localhost:8503{C.RESET}")
    print(f"   {C.WHITE}🔌 API Backend     → {C.CYAN}http://localhost:8000{C.RESET}")
    print(f"   {C.WHITE}📖 API Docs        → {C.CYAN}http://localhost:8000/docs{C.RESET}")
    divider()
    print(f"\n   {C.DIM}Close individual windows to stop services.{C.RESET}\n")
    