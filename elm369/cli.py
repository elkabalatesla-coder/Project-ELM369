import argparse
import json
from .core import initialize, verify, checkpoint, MODULES
from .intelligence import qbit, qstate, rolling_logic, critical_thinking, observable_workflow, random_protocol, artifact_record

def dump(obj):
    print(json.dumps(obj, indent=2, ensure_ascii=False))

def main():
    p = argparse.ArgumentParser(prog="elm369", description="ELM369 Termux control utility")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init")
    sub.add_parser("verify")
    cp = sub.add_parser("checkpoint"); cp.add_argument("--note", default="Manual checkpoint")
    sub.add_parser("registry")
    a = sub.add_parser("analyze")
    a.add_argument("--claim", required=True)
    a.add_argument("--evidence", type=float, required=True)
    a.add_argument("--confidence", type=float, required=True)
    a.add_argument("--impact", type=float, required=True)
    a.add_argument("--risk", type=float, required=True)
    a.add_argument("--logic", type=float, default=.5)
    a.add_argument("--learning", type=float, default=.5)
    a.add_argument("--exploration", type=float, default=.5)
    a.add_argument("--memory", type=float, default=.5)
    w = sub.add_parser("workflow"); w.add_argument("--observation", required=True); w.add_argument("--evidence", action="append", default=[])
    r = sub.add_parser("random"); r.add_argument("--seed", type=int, required=True); r.add_argument("--count", type=int, default=5); r.add_argument("--enable", action="store_true")
    l = sub.add_parser("logic"); l.add_argument("--observation", required=True)
    c = sub.add_parser("critical"); c.add_argument("--claim", required=True); c.add_argument("--evidence-item", action="append", default=[]); c.add_argument("--alternative", action="append", default=[])
    ar = sub.add_parser("artifact-hash"); ar.add_argument("path")
    args = p.parse_args()
    try:
        if args.cmd == "init":
            print(f"Initialized/checked workspace: {initialize()}")
        elif args.cmd == "verify":
            ok, messages = verify()
            dump({"integrity": "PASS" if ok else "FAIL", "messages": messages})
            return 0 if ok else 1
        elif args.cmd == "checkpoint":
            dump(checkpoint(args.note))
        elif args.cmd == "registry":
            dump(MODULES)
        elif args.cmd == "analyze":
            dump({
                "claim_review": critical_thinking(args.claim),
                "qbit": qbit(args.evidence, args.confidence, args.impact, args.risk),
                "qstate": qstate(args.logic, args.learning, args.exploration, args.memory),
                "interpretation": "Heuristic decision-support scores; not probabilities or authorization.",
            })
        elif args.cmd == "workflow":
            dump(observable_workflow(args.observation, args.evidence))
        elif args.cmd == "random":
            dump(random_protocol(args.seed, args.count, enabled=args.enable))
        elif args.cmd == "logic":
            dump(rolling_logic(args.observation))
        elif args.cmd == "critical":
            dump(critical_thinking(args.claim, args.evidence_item, args.alternative))
        elif args.cmd == "artifact-hash":
            dump(artifact_record(args.path))
    except Exception as exc:
        print(f"ERROR: {exc}")
        return 2
    return 0
