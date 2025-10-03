import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GroupKFold

def train_random_forest(X, y, groups, n_estimators=100, max_depth=None):
    """Train a Random Forest model with GroupKFold cross-validation."""
    gkf = GroupKFold(n_splits=5)
    model = RandomForestRegressor(
        n_estimators=n_estimators,
        max_depth=max_depth,
        n_jobs=-1,
        random_state=42
    )
    for train_idx, test_idx in gkf.split(X, y, groups):
        model.fit(X.iloc[train_idx], y.iloc[train_idx])
    return model

def save_model(model, path, feature_names=None):
    """Save model + its feature names together in one package."""
    package = {"model": model, "feature_names": feature_names}
    joblib.dump(package, path)
    print(f"✅ Model saved to {path}")

def load_model(path):
    """Load model + feature names (backward compatible with old pickles)."""
    package = joblib.load(path)
    if isinstance(package, dict):
        return package["model"], package.get("feature_names", None)
    else:  # fallback if it's an old pickle
        return package, None
