from itertools import product

from Sentence import Sentence, And
from inference.resolution import resolution_entails as _resolution_entails


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

    def entails(self, query: Sentence) -> bool:
        """Check if this knowledge base entails the query using resolution."""
        return _resolution_entails(self, query)


def check_entailment_brute_force(left: Sentence, right: Sentence) -> bool:
    atoms = left.collect_atoms() | right.collect_atoms()

    for values in product([False, True], repeat=len(atoms)):
        world = dict(zip(atoms, values))
        if left.evaluate(world) and not right.evaluate(world):
            return False

    return True