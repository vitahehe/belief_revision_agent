from KnowledgeBase import check_entailment_brute_force, KnowledgeBase
from Sentence import Atom, Not, And, Or, Implies, Biconditional


"""Some tests, not important"""

P = Atom("P")
Q = Atom("Q")
R = Atom("R")

s1 = And(P, Q)
s2 = Or(P, R)
s3 = Implies(Q, R)
s4 = Biconditional(P, R)
s5 = Not(P)

world1 = {"P": True, "Q": True, "R": False}
world2 = {"P": False, "Q": True, "R": True}
world3 = {"P": True, "Q": False, "R": True}

sentences = [s1, s2, s3, s4, s5]
worlds = [world1, world2, world3]

for i, world in enumerate(worlds, start=1):
    print(f"World {i}: {world}")
    for s in sentences:
        print(f"{s} = {s.evaluate(world)}")
    print()

ent1 = check_entailment_brute_force(s1, P)
ent2 = check_entailment_brute_force(s2, R)
ent3 = check_entailment_brute_force(s3, R)
ent4 = check_entailment_brute_force(s4, P)
ent5 = check_entailment_brute_force(s5, Q)

entailments = [ent1, ent2, ent3, ent4, ent5]
for i, e in enumerate(entailments, start=1):
    print(f"Entailment {i}: {e}")