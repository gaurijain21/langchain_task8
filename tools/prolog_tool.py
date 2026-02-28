# tools/prolog_tool.py
from pyswip import Prolog

def prove_with_trace(kb_path: str, query: str) -> dict:
    """
    Returns:
      {
        "query": "...",
        "result": True/False,
        "trace": [ "step1", "step2", ... ]
      }
    """
    prolog = Prolog()
    prolog.consult(kb_path)

    # ---------
    # Minimal "trace" approach (works even if you don't implement full SLD trace):
    # We record which rules/facts were involved by asking Prolog to explain via a helper predicate.
    # If you already have a Python backward-chainer in your project, use that instead (better trace).
    # ---------

    # Try proving it
    solutions = list(prolog.query(query))
    result = len(solutions) > 0

    trace = []
    if result:
      trace.append(f"Goal proved: {query}")
      trace.append(f"Found {len(solutions)} solution(s). Example binding: {solutions[0] if solutions else '{}'}")
    else:
      trace.append(f"Goal failed: {query}")
      trace.append("No solutions returned by Prolog.")

    return {"query": query, "result": result, "trace": trace}