import re
import pandas as pd
import numpy as np

ELEMENTS = ["Al","Al2O3","Si","Fe","Mg","Cu","Zn","Mn","Ni","Ca","Na","K","Ti"]

def validate_composition(comp):
    cleaned = {}
    errors = []
    for k in ELEMENTS:
        v = comp.get(k, 0)
        try:
            v = float(v or 0)
        except Exception:
            errors.append(f"{k} must be numeric")
            v = 0
        if v < 0:
            errors.append(f"{k} cannot be negative")
        cleaned[k] = v
    if sum(cleaned.values()) <= 0:
        errors.append("At least one composition value must be greater than zero")
    return len(errors) == 0, cleaned, errors

def _norm(s):
    return re.sub(r"[^a-z0-9]", "", str(s).lower())

def map_uploaded_columns_to_composition(df):
    if df is None or df.empty:
        return {}
    row = df.iloc[0].to_dict()
    out = {}
    for el in ELEMENTS:
        candidates = [el, el.lower(), f"{el}%", f"{el}_pct", f"{el}_percent", f"{el} %"]
        target = _norm(el)
        for col, val in row.items():
            n = _norm(col)
            if n == target or n == target + "pct" or n == target + "percent":
                try:
                    out[el] = float(val)
                except Exception:
                    pass
                break
    # common aliases
    aliases = {"aluminium":"Al","aluminum":"Al","silicon":"Si","iron":"Fe","magnesium":"Mg",
               "copper":"Cu","zinc":"Zn","alumina":"Al2O3","aluminiumoxide":"Al2O3"}
    for col, val in row.items():
        n = _norm(col)
        if n in aliases and aliases[n] not in out:
            try: out[aliases[n]] = float(val)
            except Exception: pass
    return out

def check_dataset_quality(df):
    return {
        "num_samples": int(len(df)),
        "num_features": int(max(0, len(df.columns)-2)),
        "missing_values": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum())
    }
