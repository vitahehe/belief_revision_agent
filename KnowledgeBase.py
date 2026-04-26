from itertools import product

from Sentence import Sentence, And
from inference.resolution import resolution_entails as _resolution_entails
from inference.cnf import to_cnf as _to_cnf, extract_clauses as _extract_clauses


def _normalize_sentence(sentence: Sentence) -> str:
    """
    Return a stable-ish normalized string for duplicate detection.

    This codebase does not yet have a dedicated parser/pretty-printer/normalizer
    module. For now we normalize via repr() and whitespace removal.
    """
    return "".join(repr(sentence).split())


class BeliefEntry:
    """
    Belief record with metadata needed for priority-based contraction.

    This intentionally mirrors the README contract, but uses the existing
    `Sentence` AST as the formula representation.
    """

    def __init__(
        self,
        *,
        belief_id: str,
        sentence: Sentence,
        priority: int,
        insertion_order: int,
    ):
        self.id = belief_id
        self.formula_str = repr(sentence)
        self.normalized_formula_str = _normalize_sentence(sentence)
        self.formula_ast = sentence
        self.sentence = sentence  # alias used by some inference helpers
        self.priority = int(priority)
        self.insertion_order = int(insertion_order)

    def __repr__(self) -> str:
        return (
            f"BeliefEntry(id={self.id!r}, priority={self.priority}, "
            f"insertion_order={self.insertion_order}, formula={self.formula_str!r})"
        )


class KnowledgeBase:
    def __init__(self, sentences: list[Sentence] | None = None, entries: list[BeliefEntry] | None = None):
        """
        Backwards compatible constructor.

        - Old code path: KnowledgeBase([Sentence, ...]) populates `entries` with
          default priorities and insertion order.
        - New code path: KnowledgeBase(entries=[BeliefEntry, ...]) uses the
          provided belief records.
        """
        if entries is not None and sentences is not None:
            raise ValueError("Provide either sentences or entries, not both.")

        if entries is not None:
            self.entries = list(entries)
        else:
            sentences = list(sentences or [])
            self.entries = [
                BeliefEntry(
                    belief_id=f"b{i+1}",
                    sentence=s,
                    priority=0,
                    insertion_order=i,
                )
                for i, s in enumerate(sentences)
            ]

        # Keep the old attribute name working for modules/tests.
        self.sentences = [e.formula_ast for e in self.entries]

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

    def to_clause_set(self) -> set[frozenset[str]]:
        """
        Return this KB as a clause-set (CNF) in the agreed format.

        Note: This is a *lossy* view of the KB (it flattens all stored sentences
        into CNF clauses).
        """
        all_clauses: set[frozenset[str]] = set()
        for sent in self.sentences:
            cnf = _to_cnf(sent)
            all_clauses |= _extract_clauses(cnf)
        return all_clauses

    def to_clause_list(self) -> list[frozenset[str]]:
        """Convenience wrapper around `to_clause_set()` with deterministic order."""
        return sorted(self.to_clause_set(), key=lambda c: (len(c), sorted(c)))

    def list_beliefs(self) -> list[BeliefEntry]:
        return list(self.entries)

    def copy(self) -> "KnowledgeBase":
        return KnowledgeBase(entries=list(self.entries))

    def contains_sentence(self, sentence: Sentence) -> bool:
        norm = _normalize_sentence(sentence)
        return any(e.normalized_formula_str == norm for e in self.entries)

    def expand(self, sentence: Sentence, priority: int) -> "KnowledgeBase":
        """
        Expansion ( + ): add sentence unless it's a duplicate.

        Priority convention: larger = more entrenched.
        """
        if self.contains_sentence(sentence):
            return self.copy()

        next_order = (max((e.insertion_order for e in self.entries), default=-1) + 1)
        next_id_num = (max((int(e.id[1:]) for e in self.entries if e.id.startswith("b") and e.id[1:].isdigit()), default=0) + 1)
        new_entry = BeliefEntry(
            belief_id=f"b{next_id_num}",
            sentence=sentence,
            priority=priority,
            insertion_order=next_order,
        )
        return KnowledgeBase(entries=[*self.entries, new_entry])

    def contract(self, sentence: Sentence) -> tuple["KnowledgeBase", list[BeliefEntry]]:
        """
        Priority-based contraction ( ÷ ) by a sentence `phi`.

        If KB entails `phi`, remove beliefs in increasing priority order. Ties are
        broken by removing the newest belief first (higher insertion_order).

        Returns:
            (new_kb, removed_entries)
        """
        kb = self.copy()
        removed: list[BeliefEntry] = []

        if not kb.entails(sentence):
            return kb, removed

        # Removal order: lowest priority first, and for same priority remove newest first.
        removal_order = sorted(
            kb.entries,
            key=lambda e: (e.priority, -e.insertion_order),
        )

        for entry in removal_order:
            if not kb.entails(sentence):
                break

            kb.entries = [e for e in kb.entries if e.id != entry.id]
            kb.sentences = [e.formula_ast for e in kb.entries]
            removed.append(entry)

        return kb, removed

    def revise(self, sentence: Sentence, priority: int) -> tuple["KnowledgeBase", list[BeliefEntry], BeliefEntry | None]:
        """
        Revision ( * ): KB * phi = (KB ÷ ~phi) + phi

        Returns:
            (new_kb, removed_entries, added_entry_or_None)
        """
        from Sentence import Not

        contracted, removed = self.contract(Not(sentence))
        expanded = contracted.expand(sentence, priority=priority)

        added = None
        if not contracted.contains_sentence(sentence) and expanded.contains_sentence(sentence):
            # last entry is the added one
            added = expanded.entries[-1] if expanded.entries else None

        return expanded, removed, added


def check_entailment_brute_force(left: Sentence, right: Sentence) -> bool:
    atoms = left.collect_atoms() | right.collect_atoms()

    for values in product([False, True], repeat=len(atoms)):
        world = dict(zip(atoms, values))
        if left.evaluate(world) and not right.evaluate(world):
            return False

    return True