# 🏦 VaultSense — Secure Financial Monitoring System
**Manipal University Jaipur · Major Project · 2026**

---

## 📌 Project Overview
VaultSense is an AI-powered financial fraud detection system 
that combines:
- **Hybrid ML Model** (Isolation Forest + Random Forest) — 83.68% F1 Score
- **Blockchain Verification** — SHA-256 tamper-proof transaction logging
- **Behavioral Profiling** — Per-user spending pattern analysis
- **Real-time Monitoring** — Live security dashboard
- **OTP Verification** — Suspicious transactions trigger verification

---

## 🏗️ Project Structure
```
MajorProject/
├── blockchain/         ← SHA-256 blockchain logger
├── data/               ← Kaggle credit card fraud dataset
├── models/             ← Trained ML models
├── api/                ← FastAPI REST backend
├── profiles/           ← User behavioral profiles
├── dashboard/          ← Streamlit apps
│   ├── user_app.py     ← Banking app (port 8501)
│   └── security_app.py ← Security dashboard (port 8502)
├── utils/              ← Helper functions
├── main.py             ← Single launcher
└── requirements.txt    ← Dependencies
```

---

## ⚙️ Setup & Installation

### 1. Clone / Download the project
```bash
cd C:\Users\rdeva\OneDrive\Desktop\MajorProject
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Download Dataset
- Download from: https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud
- Place `creditcard.csv` in the `data/` folder

### 4. Train the ML Model
```bash
python models/fraud_detector.py
```

### 5. Build User Profiles
```bash
python profiles/user_profiler.py
```

### 6. Launch Everything
```bash
python main.py
```

---

## 🌐 Access Points
| Service | URL |
|---|---|
| 🏦 Banking App | http://localhost:8501 |
| 🛡️ Security Dashboard | http://localhost:8502 |
| 🔌 API Backend | http://localhost:8000 |
| 📖 API Docs | http://localhost:8000/docs |

---

## 🤖 ML Model Details
| Model | Role | Weight |
|---|---|---|
| Random Forest | Supervised fraud detection | 55% |
| Isolation Forest | Unsupervised anomaly detection | 20% |
| Rule Engine | Explainable rule-based checks | 15% |
| Behavioral Profiler | Per-user deviation detection | 10% |

**Results:**
- Precision: 89.38%
- Recall: 78.66%
- F1 Score: 83.68%

---

## ⛓️ Blockchain Details
- Algorithm: SHA-256
- Proof of Work: difficulty = 2
- Each transaction → immutable block
- Chain validation on every request

---

## 🔐 Risk Scoring
| Score | Status | Action |
|---|---|---|
| 0 — 34 | ✅ SAFE | Approved instantly |
| 35 — 64 | ⚠️ SUSPICIOUS | OTP verification required |
| 65 — 100 | 🚨 FRAUD | Blocked + security alerted |

---

## 👥 Team
- Manipal University Jaipur
- Major Project 2026