import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "dataset.csv")
FEATURES = ["Al","Al2O3","Si","Fe","Mg","Cu","Zn","Mn","Ni","Ca","Na","K","Ti"]

def ensure_dataset_exists():
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    if os.path.exists(DATA_PATH):
        return
    rng = np.random.default_rng(42)
    rows = []
    for i in range(40):
        al = rng.uniform(45, 75); al2 = rng.uniform(15, 40)
        si = rng.uniform(1, 5); fe = rng.uniform(0.1, 1.5); mg = rng.uniform(.5, 3)
        cu = rng.uniform(.05, .6); zn = rng.uniform(.05, .5)
        mn = rng.uniform(.05, .5); ni = rng.uniform(.01, .15); ca = rng.uniform(.1, 2)
        na = rng.uniform(.05, .8); k = rng.uniform(.01, .3); ti = rng.uniform(.01, .3)
        metal = np.clip(0.72*al + 0.7*si - 1.8*fe - .8*mg + rng.normal(0,2), 5, 90)
        alumina = np.clip(0.58*al2 + .2*al - 1.0*si - .5*fe + rng.normal(0,2), 3, 75)
        rows.append([al,al2,si,fe,mg,cu,zn,mn,ni,ca,na,k,ti,metal,alumina])
    cols = FEATURES + ["metal_recovery","alumina_recovery"]
    pd.DataFrame(rows, columns=cols).to_csv(DATA_PATH, index=False)

def load_dataset():
    ensure_dataset_exists()
    return pd.read_csv(DATA_PATH)

def is_demo_dataset(df):
    return len(df) <= 100 and "metal_recovery" in df.columns and "alumina_recovery" in df.columns

def _model(kind):
    if kind == "Linear Regression": return LinearRegression()
    if kind == "Gradient Boosting": return GradientBoostingRegressor(random_state=42, n_estimators=120)
    return RandomForestRegressor(random_state=42, n_estimators=150, max_depth=6)

def train_and_evaluate(df, model_type="Random Forest"):
    if not all(c in df.columns for c in FEATURES+["metal_recovery","alumina_recovery"]) or len(df) < 8:
        return {"sufficient": False, "n_samples": len(df)}
    x = df[FEATURES].fillna(0); ym = df["metal_recovery"]; ya = df["alumina_recovery"]
    xt, xv, ymt, ymv = train_test_split(x, ym, test_size=.25, random_state=42)
    _, _, yat, yav = train_test_split(x, ya, test_size=.25, random_state=42)
    mm, am = _model(model_type), _model(model_type)
    mm.fit(xt, ymt); am.fit(xt, yat)
    pm, pa = mm.predict(xv), am.predict(xv)
    def metrics(y,p):
        return {"r2": float(r2_score(y,p)), "mae": float(mean_absolute_error(y,p)),
                "rmse": float(np.sqrt(mean_squared_error(y,p)))}
    return {"sufficient": True, "n_samples": len(df), "metal": metrics(ymv,pm),
            "alumina": metrics(yav,pa), "metal_model": mm, "alumina_model": am}

def predict_recovery(trained, composition):
    x = pd.DataFrame([[float(composition.get(c,0)) for c in FEATURES]], columns=FEATURES)
    return float(np.clip(trained["metal_model"].predict(x)[0],0,100)), float(np.clip(trained["alumina_model"].predict(x)[0],0,100))

def recovery_category(metal, alumina):
    avg = (metal + alumina) / 2
    return "Excellent" if avg >= 75 else "Good" if avg >= 55 else "Moderate" if avg >= 35 else "Low"

def recommend_method(comp, metal, alumina):
    if comp.get("Al",0) >= 60 and comp.get("Al2O3",0) >= 25:
        return "Mechanical separation + salt-free thermal treatment", "High aluminium and alumina content supports recovery-focused separation."
    if comp.get("Si",0) > 4:
        return "Controlled thermal treatment + flux optimization", "Higher silicon can reduce recovery; process control is recommended."
    return "Mechanical separation + controlled thermal treatment", "Balanced composition suggests a conventional recovery route."
