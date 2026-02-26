from fol_bc import Rule, KnowledgeBase

def build_kb():
    rules = [
        # FACTS
        Rule(("parent","john","mary"), ()),
        Rule(("parent","mary","sue"), ()),
        Rule(("parent","john","alex"), ()),
        Rule(("parent","alex","david"), ()),
        Rule(("parent","david","lily"), ()),

        Rule(("male","john"), ()),
        Rule(("male","alex"), ()),
        Rule(("male","david"), ()),

        Rule(("female","mary"), ()),
        Rule(("female","sue"), ()),
        Rule(("female","lily"), ()),
        Rule(("female","anna"), ()),

        Rule(("married","john","anna"), ()),
        Rule(("married","anna","john"), ()),

        # RULES
        Rule(("ancestor","?x","?y"), (("parent","?x","?y"),)),
        Rule(("ancestor","?x","?y"), (("parent","?x","?z"), ("ancestor","?z","?y"))),

        Rule(("grandparent","?x","?y"), (("parent","?x","?z"), ("parent","?z","?y"))),

        Rule(("sibling","?x","?y"), (("parent","?z","?x"), ("parent","?z","?y"))),  # note: no X != Y check here unless you implemented it

        Rule(("mother","?x","?y"), (("parent","?x","?y"), ("female","?x"))),
        Rule(("father","?x","?y"), (("parent","?x","?y"), ("male","?x"))),

        Rule(("spouse","?x","?y"), (("married","?x","?y"),)),

        Rule(("brother","?x","?y"), (("sibling","?x","?y"), ("male","?x"))),
    ]
    return KnowledgeBase(rules)
