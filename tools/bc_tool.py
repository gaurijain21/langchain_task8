# tools/bc_tool.py
from __future__ import annotations
from typing import List, Dict
import re

from fol_bc import KnowledgeBase, ask
from kb.family_kb import build_kb


def parse_query(q: str):
    """
    Converts:
      "ancestor(john, sue)" -> ("ancestor", "john", "sue")
      "ancestor(john, ?who)" -> ("ancestor", "john", "?who")
    """
    q = q.strip()
    q = q[:-1] if q.endswith(".") else q  # allow trailing period
    m = re.match(r"^([a-zA-Z_]\w*)\s*\(\s*(.*?)\s*\)\s*$", q)
    if not m:
        raise ValueError(f"Bad query format: {q} (expected like ancestor(john, sue))")

    pred = m.group(1)
    args_str = m.group(2).strip()

    if args_str == "":
        return (pred,)

    args = [a.strip() for a in args_str.split(",")]
    return tuple([pred] + args)

# tools/bc_tool.py (keep your parse_query as-is)

from fol_bc import ask

def rag_filter_rules_for_query(kb, query_predicate):
    """
    Better lightweight RAG:
    1) Keep rules that can prove the goal predicate (head matches name+arity)
    2) Also keep any rules/facts needed by their bodies (predicate dependencies)
       (one-hop closure + recursion-safe)
    """
    qname, *qargs = query_predicate
    want = set([(qname, len(qargs))])  # predicates we must keep: (name, arity)

    selected = []
    changed = True

    while changed:
        changed = False
        # scan all rules; if its head is in want, select it and add its body predicates to want
        for r in kb.rules:
            rname, *rargs = r.head
            head_sig = (rname, len(rargs))
            if head_sig in want and r not in selected:
                selected.append(r)
                # add body predicate signatures
                for b in r.body:
                    bname, *bargs = b
                    sig = (bname, len(bargs))
                    if sig not in want:
                        want.add(sig)
                        changed = True

    from fol_bc import KnowledgeBase
    return KnowledgeBase(selected)

def prove_with_bc(query_str: str) -> dict:
    query_pred = parse_query(query_str)

    kb_full = build_kb()

    # RAG step (optional, but matches checklist)
    kb = rag_filter_rules_for_query(kb_full, query_pred)

    solutions = ask(kb, query_pred)
    result = len(solutions) > 0

    trace = []
    if result:
        trace.append(f"Goal proved: {query_pred}")
        trace.append(f"Solutions found: {len(solutions)}")
        trace.append(f"Example substitution: {solutions[0]}")
    else:
        trace.append(f"Goal failed: {query_pred}")
        trace.append("No substitutions returned.")

    return {
        "query": query_str,
        "parsed_query": query_pred,
        "result": result,
        "solutions": solutions,
        "trace": trace,
        "rag_used_rules": len(kb.rules),
        "kb_total_rules": len(kb_full.rules),
    }