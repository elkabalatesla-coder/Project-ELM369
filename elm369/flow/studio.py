"""Studio+."""
import hashlib
import json
def ingest(clip):
    cid = hashlib.sha256(clip.encode()).hexdigest()
    cid = "elm369-clip-" + cid[:12]
    return {"clip_id": cid, "source": clip, "status": "INGESTED"}
def angles(clip):
    out = []
    names = ["wide", "medium", "close", "over-shoulder"]
    for a in names:
        key = clip["clip_id"] + ":" + a
        sd = hashlib.sha256(key.encode()).hexdigest()
        sd = int(sd[:8], 16)
        out.append({"angle": a, "seed": sd, "locked": True})
    return {"count": len(out), "angles": out}
def upscale(clip):
    return {"clip_id": clip["clip_id"], "target": "1080p", "status": "READY"}
def verify(clip, motion=0.02, lip=12.0):
    m_ok = motion <= 0.05
    l_ok = lip <= 40
    failed = []
    if not m_ok:
        failed.append("motion")
    if not l_ok:
        failed.append("lip_sync")
    st = "PENDING_REVIEW"
    if failed:
        st = "NOT_GRANTED"
    return {"clip_id": clip["clip_id"], "motion": motion, "lip": lip, "failed": failed, "status": st}
def full_run(clip):
    c = ingest(clip)
    a = angles(c)
    u = upscale(c)
    v = verify(c)
    return {"clip": c, "angles": a, "upscale": u, "verify": v}
if __name__ == "__main__":
    print(json.dumps(full_run("phone_take_001.mp4"), indent=2))
