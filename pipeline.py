import os
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import xgboost as xgb

# -----------------------
# Data loading + features
# -----------------------
def load_fd001(path="data/FD001.txt"):
    col_names = (
        ["engine_id", "cycle", "setting_1", "setting_2", "setting_3"]
        + [f"sensor_{i}" for i in range(1, 22)]
    )
    df = pd.read_csv(path, sep=r"\s+", header=None, names=col_names)
    return df

def add_rul(df):
    rul = df.groupby("engine_id")["cycle"].transform("max") - df["cycle"]
    df["RUL"] = rul
    return df

def add_features(df):
    feat_df = df.copy()
    for col in [c for c in df.columns if "sensor_" in c]:
        feat_df[f"{col}_rollmean_w5"] = df.groupby("engine_id")[col].transform(
            lambda x: x.rolling(window=5, min_periods=1).mean()
        )
    return feat_df

# -----------------------
# Train + save
# -----------------------
def train_and_report():
    print("📂 Loading data...")
    df = load_fd001()
    df = add_rul(df)
    df_feat = add_features(df)

    X = df_feat.drop(columns=["RUL"])
    y = df_feat["RUL"]

    # ⚠️ Exclude IDs & raw cycle count (not useful for model)
    drop_cols = ["engine_id", "cycle"]
    X = X.drop(columns=drop_cols)
    feature_names = X.columns.tolist()

    # Train Random Forest
    print("🌲 Training Random Forest...")
    rf = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
    rf.fit(X, y)
    y_pred_rf = rf.predict(X)
    rmse_rf = mean_squared_error(y, y_pred_rf) ** 0.5

    # Train XGBoost
    print("⚡ Training XGBoost...")
    xgbr = xgb.XGBRegressor(
        n_estimators=300, learning_rate=0.05, max_depth=6, random_state=42, n_jobs=-1
    )
    xgbr.fit(X, y)
    y_pred_xgb = xgbr.predict(X)
    rmse_xgb = mean_squared_error(y, y_pred_xgb) ** 0.5

    # Ensure models dir exists
    os.makedirs("models", exist_ok=True)

    # Save models + features
    joblib.dump(rf, "models/rf_model.pkl")
    joblib.dump(feature_names, "models/rf_features.pkl")
    joblib.dump(xgbr, "models/xgb_model.pkl")
    joblib.dump(feature_names, "models/xgb_features.pkl")

    # Report
    os.makedirs("reports", exist_ok=True)
    with open("reports/training_results.txt", "w", encoding="utf-8") as f:
        f.write("Model Results:\n")
        f.write(f"Random Forest RMSE: {rmse_rf:.2f}\n")
        f.write(f"XGBoost RMSE: {rmse_xgb:.2f}\n")

    print("✅ Training complete! Results written to reports/training_results.txt")

# -----------------------
# Run from command line
# -----------------------
if __name__ == "__main__":
    train_and_report()
def run_pipeline(df):
    """
    Simple demo pipeline.
    Takes a dataframe with sensor features and returns
    a dictionary with compliance analysis results.
    """
    # For demo: pretend to analyze the data
    risk_score = 78  # placeholder number
    violations = ["GDPR", "SOC2", "FAA"]  # fake issues
    suggestions = [
        "Encrypt user data at rest",
        "Add access control logging",
        "Update FAA compliance checklist"
    ]

    results = {
        "document": "sample_input.csv",
        "risk_score": risk_score,
        "violations": violations,
        "suggestions": suggestions
    }
    return results

if uploaded_file is not None:
    predictions = run_pipeline(data)  # wrapper around your model
    st.line_chart(predictions)
