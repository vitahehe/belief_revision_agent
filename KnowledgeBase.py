from itertools import product

from Sentence import Sentence, And


class KnowledgeBase:
    def __init__(self, sentences: list[Sentence]):
        self.sentences = sentences

    def convert_to_cnf(self):
        return self.join_clauses().to_cnf()


    def join_clauses(self):
        if len(self.sentences) == 0:
            print("nope")

        if len(self.sentences) == 1:
            return self.sentences[0]

        and_clause = And(self.sentences[0], self.sentences[1])

        for s in range(2, len(self.sentences)):
           and_clause = and_clause.add_clause(self.sentences[s])

        return and_clause


def check_entailment_brute_force(left: Sentence, right: Sentence) -> bool:
    atoms = left.collect_atoms() | right.collect_atoms()

    for values in product([False, True], repeat=len(atoms)):
        world = dict(zip(atoms, values))
        if left.evaluate(world) and not right.evaluate(world):
            return False

    return True