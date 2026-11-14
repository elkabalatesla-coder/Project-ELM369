"""Poster+."""
import hashlib
import json
import math
def cosine(a, b):
    dot = 0.0
    for x, y in zip(a, b):
        dot += x * y
    na = 0.0
    for x in a:
        na += x * x
    nb = 0.0
    for y in b:
        nb += y * y
    na = math.sqrt(na)
    nb = math.sqrt(nb)
    if na == 0 or nb == 0:
        return 0.0
    return round(dot / (na * nb), 3)
def vec(text):
    out = []
    for i in range(16):
        key = text + ":" + str(i)
        h = hashlib.sha256(key.encode()).hexdigest()
        v = int(h[:8], 16)
        out.append(round(((v % 1000) / 1000.0) * 2 - 1, 3))
    return out
def brief(concept):
    return {"concept": concept, "status": "BRIEF_READY"}
def lock_style(refs):
    vecs = []
    for t in refs:
        vecs.append(vec(t))
    avg = []
    for i in range(16):
        s = 0.0
        for v in vecs:
            s += v[i]
        avg.append(round(s / len(vecs), 3))
    key = "|".join(refs)
    sid = hashlib.sha256(key.encode()).hexdigest()
    sid = "elm369-style-" + sid[:12]
    return {"style_id": sid, "vector": avg}
def gen_set(br, lk):
    posts = []
    base = lk["vector"]
    for i in range(6):
        txt = br["concept"] + ":v" + str(i)
        v = vec(txt)
        bl = []
        for b, x in zip(base, v):
            bl.append(round(0.85 * b + 0.15 * x, 3))
        sc = cosine(bl, base)
        ok = sc >= 0.85
        posts.append({"index": i + 1, "score": sc, "status": "READY" if ok else "DRIFT"})
    return {"count": len(posts), "posters": posts}
def full_run(concept, refs):
    br = brief(concept)
    lk = lock_style(refs)
    gn = gen_set(br, lk)
    return {"brief": br, "lock": lk, "gen": gn}
if __name__ == "__main__":
    demo = full_run("beach", ["cinematic beach poster"])
    print(json.dumps(demo, indent=2))
