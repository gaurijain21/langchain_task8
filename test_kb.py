from fol_bc import ask
from kb.family_kb import build_kb

kb = build_kb()

print("ancestor(john, lily):", ask(kb, ("ancestor","john","lily")))
print("grandparent(john, sue):", ask(kb, ("grandparent","john","sue")))
print("mother(mary, sue):", ask(kb, ("mother","mary","sue")))
print("ancestor(john, ?who):", ask(kb, ("ancestor","john","?who")))
