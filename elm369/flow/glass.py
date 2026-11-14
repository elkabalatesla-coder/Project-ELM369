"""Glass+."""
import json
import math
def snell(a, n1=1.0, n2=1.52):
    t = math.radians(a)
    s = (n1 / n2) * math.sin(t)
    if abs(s) > 1.0:
        return None
    return round(math.degrees(math.asin(s)), 3)
def lens():
    return {
        "type": "prism",
        "n": {"r": 1.51, "g": 1.52, "b": 1.53},
        "angle": 45.0,
        "inten": 0.8,
    }
def refract(ref, ln):
    n = ln["n"]
    a = ln["angle"]
    d = {}
    d["red"] = snell(a, 1.0, n["r"])
    d["green"] = snell(a, 1.0, n["g"])
    d["blue"] = snell(a, 1.0, n["b"])
    it = ln["inten"]
    eff = {}
    eff["bloom"] = round(0.35 * it, 3)
    eff["halo"] = round(0.25 + 0.45 * it, 3)
    eff["caustic"] = round(it * 0.9, 3)
    return {"img": ref, "disp": d, "eff": eff}
def validate(r):
    d = r["disp"]
    rr = d["red"]
    gg = d["green"]
    bb = d["blue"]
    ok = rr is not None
    ok = ok and gg is not None
    ok = ok and bb is not None
    ok = ok and (rr > gg > bb)
    st = "PENDING_REVIEW"
    if not ok:
        st = "NOT_GRANTED"
    return {"plausible": ok, "status": st}
def full_run(ref):
    ln = lens()
    rf = refract(ref, ln)
    va = validate(rf)
    return {"lens": ln, "ref": rf, "val": va}
def snell_refract(a, n1=1.0, n2=1.52):
    v = snell(a, n1, n2)
    if v is None:
        return {"status": "TOTAL"}
    return {"theta2": v, "status": "REFRACTED"}
if __name__ == "__main__":
    print(json.dumps(full_run("poster-001.jpg"), indent=2))
