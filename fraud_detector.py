import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, f1_score, roc_auc_score
from imblearn.over_sampling import SMOTE
from xgboost import XGBClassifier
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import os

# ── 1. LOAD DATA ──
print("📂 Loading dataset...")
df = pd.read_csv("data/creditcard.csv")
print(f"✅ Loaded {len(df):,} transactions")
print(f"   Fraud cases    : {df['Class'].sum():,} ({df['Class'].mean()*100:.2f}%)")
print(f"   Legit cases    : {(df['Class']==0).sum():,}")

# ── 2. PREPROCESS ──
print("\n⚙️  Preprocessing data...")
features = [col for col in df.columns if col != 'Class']
X = df[features].copy()
y = df['Class'].copy()

# ── Feature Engineering ──
print("🔧 Engineering new features...")
df['Amount_log']  = np.log1p(df['Amount'])
df['hour_of_day'] = ((df['Time'] % 86400) / 3600).astype(int)
df['is_night']    = ((df['hour_of_day'] < 5) | (df['hour_of_day'] > 22)).astype(int)
df['is_micro']    = ((df['Amount'] > 0) & (df['Amount'] < 1)).astype(int)
df['is_high']     = (df['Amount'] > 1000).astype(int)

features = [col for col in df.columns if col not in ['Class']]
X = df[features].copy()
y = df['Class'].copy()

scaler = StandardScaler()
X[['Amount', 'Time', 'Amount_log']] = scaler.fit_transform(
    X[['Amount', 'Time', 'Amount_log']]
)
print("✅ Features engineered and scaled")
print(f"   Total features: {len(features)}")

# ── 3. ISOLATION FOREST (Unsupervised) ──
print("\n🤖 Training Isolation Forest...")
iso = IsolationForest(
    n_estimators=200,
    contamination=0.0017,
    max_samples='auto',
    random_state=42
)
iso.fit(X)
iso_scores = iso.decision_function(X)
iso_scores_norm = 100 * (1 - (iso_scores - iso_scores.min()) / (iso_scores.max() - iso_scores.min()))
print("✅ Isolation Forest trained!")

# ── 4. RANDOM FOREST (Supervised) ──
print("\n🌲 Training Random Forest (supervised)...")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ── Apply SMOTE to training set only ──
print("⚖️  Applying SMOTE oversampling...")
smote   = SMOTE(random_state=42, k_neighbors=5)
X_train_sm, y_train_sm = smote.fit_resample(X_train, y_train)
print(f"✅ SMOTE done — {y_train_sm.sum():,} fraud samples (was {y_train.sum():,})")

# ── Random Forest ──
print("\n🌲 Training Random Forest...")
rf = RandomForestClassifier(
    n_estimators    = 300,
    max_depth       = 25,
    min_samples_leaf= 2,
    class_weight    = 'balanced',
    random_state    = 42,
    n_jobs          = -1
)
rf.fit(X_train_sm, y_train_sm)
rf_test_pred  = rf.predict(X_test)
rf_test_proba = rf.predict_proba(X_test)[:, 1]
rf_f1         = f1_score(y_test, rf_test_pred)
rf_auc        = roc_auc_score(y_test, rf_test_proba)
print(f"✅ Random Forest — F1: {rf_f1:.4f} · AUC: {rf_auc:.4f}")

# ── XGBoost ──
print("\n⚡ Training XGBoost...")
scale_pos = (y_train == 0).sum() / (y_train == 1).sum()
xgb = XGBClassifier(
    n_estimators      = 300,
    max_depth         = 6,
    learning_rate     = 0.05,
    subsample         = 0.8,
    colsample_bytree  = 0.8,
    scale_pos_weight  = scale_pos,
    use_label_encoder = False,
    eval_metric       = 'logloss',
    random_state      = 42,
    n_jobs            = -1
)
xgb.fit(X_train_sm, y_train_sm)
xgb_test_pred  = xgb.predict(X_test)
xgb_test_proba = xgb.predict_proba(X_test)[:, 1]
xgb_f1         = f1_score(y_test, xgb_test_pred)
xgb_auc        = roc_auc_score(y_test, xgb_test_proba)
print(f"✅ XGBoost       — F1: {xgb_f1:.4f} · AUC: {xgb_auc:.4f}")

# ── Pick best model ──
if xgb_f1 >= rf_f1:
    best_model      = xgb
    best_model_name = "XGBoost"
    best_proba_full = xgb.predict_proba(X)[:, 1] * 100
    print(f"\n🏆 Best model: XGBoost (F1: {xgb_f1:.4f})")
else:
    best_model      = rf
    best_model_name = "RandomForest"
    best_proba_full = rf.predict_proba(X)[:, 1] * 100
    print(f"\n🏆 Best model: RandomForest (F1: {rf_f1:.4f})")

# Use best model scores
rf_scores_norm = best_proba_full

# ── 5. RULE-BASED CHECKS ──
print("\n📏 Applying rule-based checks...")

def rule_based_score(row):
    score = 0
    # Large amount
    if row['Amount'] > 1000:
        score += 20
    elif row['Amount'] > 500:
        score += 10
    # Odd hours (late night transactions)
    hour = (row['Time'] % 86400) / 3600
    if hour < 5 or hour > 22:
        score += 15
    # Very small amount (card testing)
    if 0 < row['Amount'] < 1:
        score += 25
    return min(score, 100)

rule_scores = df.apply(rule_based_score, axis=1).values
print("✅ Rule-based checks applied!")

# ── 6. HYBRID SCORE ──
print("\n🔀 Combining scores (Hybrid Model)...")

# Weighted combination
# Random Forest gets highest weight (supervised, most accurate)
# Isolation Forest catches unknown anomalies
# Rules catch obvious patterns
final_scores = (
    0.65 * rf_scores_norm +
    0.20 * iso_scores_norm +
    0.15 * rule_scores
)

df['risk_score'] = final_scores.round(2)

def label_transaction(score):
    if score >= 65:
        return "FRAUD"
    elif score >= 35:
        return "SUSPICIOUS"
    else:
        return "SAFE"

df['predicted_status'] = df['risk_score'].apply(label_transaction)
predicted_fraud = (df['predicted_status'] == 'FRAUD').astype(int)

# ── 7. EVALUATION ──
print("\n📈 Hybrid Model Evaluation:")
print(f"   FRAUD flagged      : {(df['predicted_status']=='FRAUD').sum():,}")
print(f"   SUSPICIOUS flagged : {(df['predicted_status']=='SUSPICIOUS').sum():,}")
print(f"   SAFE               : {(df['predicted_status']=='SAFE').sum():,}")

tp = ((y == 1) & (predicted_fraud == 1)).sum()
fp = ((y == 0) & (predicted_fraud == 1)).sum()
fn = ((y == 1) & (predicted_fraud == 0)).sum()
tn = ((y == 0) & (predicted_fraud == 0)).sum()

precision = tp / (tp + fp) if (tp + fp) > 0 else 0
recall    = tp / (tp + fn) if (tp + fn) > 0 else 0
f1        = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

print(f"\n   True Positives  : {tp:,}")
print(f"   False Positives : {fp:,}")
print(f"   False Negatives : {fn:,}")
print(f"\n   ✅ Precision     : {precision:.2%}")
print(f"   ✅ Recall        : {recall:.2%}")
print(f"   ✅ F1 Score      : {f1:.2%}")

# ── 8. VISUALIZATIONS ──
print("\n🎨 Generating visualizations...")
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.patch.set_facecolor('#040b14')

for ax in axes:
    ax.set_facecolor('#07111f')
    ax.tick_params(colors='#3d6080')
    for spine in ax.spines.values():
        spine.set_edgecolor('#0f2a45')

# Plot 1 — Risk Score Distribution
axes[0].hist(df[df['Class']==0]['risk_score'], bins=60,
             color='#00d4ff', alpha=0.6, label='Legitimate')
axes[0].hist(df[df['Class']==1]['risk_score'], bins=60,
             color='#ff3b5c', alpha=0.85, label='Fraud')
axes[0].set_title('Hybrid Risk Score Distribution', color='white', fontweight='bold')
axes[0].set_xlabel('Risk Score', color='#3d6080')
axes[0].set_ylabel('Count', color='#3d6080')
axes[0].legend(facecolor='#07111f', labelcolor='white')

# Plot 2 — Status Distribution
status_counts = df['predicted_status'].value_counts()
colors_map = {'SAFE': '#00e676', 'SUSPICIOUS': '#ffb800', 'FRAUD': '#ff3b5c'}
bar_colors = [colors_map[s] for s in status_counts.index]
axes[1].bar(status_counts.index, status_counts.values,
            color=bar_colors, edgecolor='#0f2a45', width=0.5)
axes[1].set_title('Transaction Status Distribution', color='white', fontweight='bold')
axes[1].set_xlabel('Status', color='#3d6080')
axes[1].set_ylabel('Count', color='#3d6080')
for i, (val, label) in enumerate(zip(status_counts.values, status_counts.index)):
    axes[1].text(i, val + 100, f'{val:,}', ha='center', color='white', fontsize=10)

# Plot 3 — Confusion Matrix
cm = confusion_matrix(y, predicted_fraud)
sns.heatmap(cm, annot=True, fmt='d', cmap='YlOrRd', ax=axes[2],
            xticklabels=['Legit', 'Fraud'],
            yticklabels=['Legit', 'Fraud'],
            annot_kws={'color': 'white', 'fontsize': 12})
axes[2].set_title('Confusion Matrix', color='white', fontweight='bold')
axes[2].set_xlabel('Predicted', color='#3d6080')
axes[2].set_ylabel('Actual', color='#3d6080')

plt.tight_layout()
plt.savefig('models/fraud_analysis.png', dpi=150,
            bbox_inches='tight', facecolor='#040b14')
print("✅ Saved → models/fraud_analysis.png")
plt.show()

# ── 9. SAVE MODELS ──
print("\n💾 Saving all models...")
with open('models/isolation_forest.pkl', 'wb') as f:
    pickle.dump(iso, f)
with open('models/random_forest.pkl', 'wb') as f:
    pickle.dump(rf, f)
with open('models/scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)
with open('models/feature_columns.pkl', 'wb') as f:
    pickle.dump(features, f)

with open('models/xgboost.pkl', 'wb') as f:
    pickle.dump(xgb, f)
with open('models/best_model_name.pkl', 'wb') as f:
    pickle.dump(best_model_name, f)

print("✅ isolation_forest.pkl")
print("✅ random_forest.pkl")
print("✅ xgboost.pkl")
print("✅ scaler.pkl")
print("✅ feature_columns.pkl")
print(f"\n🏆 Best model: {best_model_name}")
print(f"   RF  — F1: {rf_f1:.4f} · AUC: {rf_auc:.4f}")
print(f"   XGB — F1: {xgb_f1:.4f} · AUC: {xgb_auc:.4f}")
print("\n🎉 VaultSense Hybrid Fraud Detection Model ready!")