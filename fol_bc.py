from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Generator, Iterable, List, Tuple, Union, Optional
import itertools

Term = str
Predicate = Tuple[str, ...]  # e.g. ("Parent", "john", "mary") or ("Ancestor", "?x", "?y")
Subst = Dict[Term, Term]

@dataclass(frozen=True)
class Rule:
    head: Predicate
    body: Tuple[Predicate, ...]  # empty body => fact

class KnowledgeBase:
    def __init__(self, rules: Iterable[Rule]):
        self.rules = list(rules)

    def fetch_rules_for_goal(self, goal: Predicate) -> Iterable[Rule]:
        # match by predicate name + arity
        gname, *gargs = goal
        for r in self.rules:
            rname, *rargs = r.head
            if rname == gname and len(rargs) == len(gargs):
                yield r

def is_variable(t: Term) -> bool:
    return isinstance(t, str) and t.startswith("?")

def subst_term(theta: Subst, t: Term) -> Term:
    # chase substitution chain
    while is_variable(t) and t in theta and theta[t] != t:
        t = theta[t]
    return t

def subst_pred(theta: Subst, p: Predicate) -> Predicate:
    name = p[0]
    args = tuple(subst_term(theta, a) for a in p[1:])
    return (name, *args)

def occurs_check(v: Term, x: Term, theta: Subst) -> bool:
    # With string-only terms, occurs check is trivial (no nested structures)
    # Keep it for completeness.
    x = subst_term(theta, x)
    return v == x

def unify(x: Union[Term, Predicate], y: Union[Term, Predicate], theta: Subst) -> Optional[Subst]:
    """
    Returns a new substitution dict if unification succeeds, else None.
    """
    if theta is None:
        return None

    # If predicates, unify element-wise
    if isinstance(x, tuple) and isinstance(y, tuple):
        if len(x) != len(y):
            return None
        # unify predicate name too
        if x[0] != y[0]:
            return None
        new_theta = dict(theta)
        for xi, yi in zip(x[1:], y[1:]):
            new_theta = unify(xi, yi, new_theta)
            if new_theta is None:
                return None
        return new_theta

    # Both are terms
    if isinstance(x, str) and isinstance(y, str):
        x = subst_term(theta, x)
        y = subst_term(theta, y)

        if x == y:
            return dict(theta)

        if is_variable(x):
            return unify_var(x, y, theta)
        if is_variable(y):
            return unify_var(y, x, theta)

        # two different constants
        return None

    return None

def unify_var(v: Term, x: Term, theta: Subst) -> Optional[Subst]:
    if v in theta:
        return unify(theta[v], x, theta)
    if is_variable(x) and x in theta:
        return unify(v, theta[x], theta)
    if occurs_check(v, x, theta):
        return None
    new_theta = dict(theta)
    new_theta[v] = x
    return new_theta

_var_counter = itertools.count()

def standardize_apart(rule: Rule) -> Rule:
    """
    Rename variables in a rule to unique variables each time the rule is used.
    """
    mapping: Dict[Term, Term] = {}

    def rename_term(t: Term) -> Term:
        if is_variable(t):
            if t not in mapping:
                mapping[t] = f"{t}_{next(_var_counter)}"
            return mapping[t]
        return t

    def rename_pred(p: Predicate) -> Predicate:
        return (p[0], *tuple(rename_term(a) for a in p[1:]))

    new_head = rename_pred(rule.head)
    new_body = tuple(rename_pred(p) for p in rule.body)
    return Rule(new_head, new_body)

def bc_or(kb: KnowledgeBase, goal: Predicate, theta: Subst) -> Generator[Subst, None, None]:
    """
    Try to prove 'goal' under substitution theta by choosing a rule whose head unifies with goal.
    """
    goal = subst_pred(theta, goal)

    for rule in kb.fetch_rules_for_goal(goal):
        r = standardize_apart(rule)
        theta1 = unify(r.head, goal, theta)
        if theta1 is None:
            continue

        if len(r.body) == 0:
            # fact
            yield theta1
        else:
            yield from bc_and(kb, list(r.body), theta1)

def bc_and(kb: KnowledgeBase, goals: List[Predicate], theta: Subst) -> Generator[Subst, None, None]:
    """
    Prove all goals in the list (conjunction).
    """
    if theta is None:
        return
    if not goals:
        yield theta
        return

    first, rest = goals[0], goals[1:]
    for theta1 in bc_or(kb, first, theta):
        yield from bc_and(kb, rest, theta1)

def ask(kb: KnowledgeBase, query: Predicate) -> List[Subst]:
    """
    Return all substitutions that satisfy the query (empty list => fail).
    """
    return list(bc_or(kb, query, {}))

# ---------------------------
# Tiny sanity tests you can run locally
# ---------------------------
if __name__ == "__main__":
    rules = [
        Rule(("parent", "john", "mary"), ()),
        Rule(("parent", "mary", "sue"), ()),
        Rule(("ancestor", "?x", "?y"), (("parent", "?x", "?y"),)),
        Rule(("ancestor", "?x", "?y"), (("parent", "?x", "?z"), ("ancestor", "?z", "?y"))),
    ]
    kb = KnowledgeBase(rules)

    print("Ask ancestor(john, sue):", ask(kb, ("ancestor", "john", "sue")))
    print("Ask ancestor(john, ?who):", ask(kb, ("ancestor", "john", "?who")))