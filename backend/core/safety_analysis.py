def build_safety_summary(comp, sds_sections=None):
    concerns = []
    if comp.get("Mg",0) >= 3: concerns.append("Elevated magnesium content; avoid uncontrolled heating.")
    if comp.get("Na",0) >= 1: concerns.append("Elevated sodium content; moisture control is important.")
    if comp.get("Zn",0) >= 1: concerns.append("Elevated zinc content; verify dust/fume controls.")
    risk = "HIGH" if len(concerns) >= 2 else "MEDIUM" if concerns else "LOW"
    return {
        "risk_level": risk,
        "classification_note": "Composition-based screening only; verify with SDS/laboratory data.",
        "composition_concerns": concerns,
        "handling_advice": "Avoid generating or breathing dust. Use suitable PPE and ventilation.",
        "storage_advice": "Store dry, cool, covered and away from moisture and ignition sources.",
        "ppe_advice": "Safety glasses, protective gloves and appropriate respiratory protection.",
        "detox_treatment_advice": "Follow the verified SDS and site emergency procedure for exposure.",
        "disposal_advice": "Dispose according to applicable waste regulations.",
        "sds_available": bool(sds_sections),
        "sds_hazards_text": (sds_sections or {}).get("2","Information not available.")
    }

def industrial_applications(comp, metal, alumina):
    out=[]
    if metal >= 50: out.append("Secondary aluminium recovery")
    if alumina >= 30: out.append("Alumina-rich by-product utilization")
    if not out: out.append("Further beneficiation and controlled recovery")
    return out

def environmental_benefits():
    return ["Reduces aluminium losses to landfill", "Supports resource recovery", "Can reduce demand for primary aluminium production"]
