from typing import Dict, Tuple

from DataStructure import LiteralStore

class Sentence:
    def evaluate(self, world: Dict[str, bool]) -> bool:
        """Evaluate the sentence under the provided world.

        Args:
            world: A mapping from atom names (str) to boolean truth values.

        Returns:
            The boolean value of this sentence in the given world.

        Raises:
            NotImplementedError: Implemented by concrete subclasses.
        """
        raise NotImplementedError

    def collect_atoms(self) -> set[str]:
        """Collect the set of atomic proposition names used in this sentence.

        Returns:
            A set of strings representing atom names present in the sentence.
        """
        raise NotImplementedError

    def to_cnf(self):
        """Convert the sentence to conjunctive normal form (CNF).

        This is a convenience wrapper that applies the standard three-step
        transformation: eliminate implications, push negations inward (NNF),
        and distribute OR over AND to reach CNF.

        Returns:
            A Sentence object representing an equivalent sentence in CNF.
        """
        return self.eliminate_implications().push_not().distribute()

    def eliminate_implications(self):
        """Return an equivalent sentence with implications/biconditionals removed.

        Implementations should replace Implies and Biconditional constructs with
        combinations of And/Or/Not so further transformations can proceed.
        """
        raise NotImplementedError

    def push_not(self):
        """Push negations inward to achieve negation normal form (NNF).

        This method should apply De Morgan's laws and eliminate double negation
        so that Not only appears directly above Atoms.
        """
        raise NotImplementedError

    def distribute(self):
        """Perform distribution step to move towards CNF.

        Specifically, distribute Or over And when necessary. The result should
        be an equivalent sentence where top-level structure is a conjunction of
        disjunctions (i.e., CNF).
        """
        raise NotImplementedError

    def is_literal(self):
        """Return True if this sentence is a literal (an atom or negated atom).

        Default returns False; concrete literal classes override to return True.
        """
        return False

    def collect_literals(self, literal_store: LiteralStore):
        """Collect literal occurrences into a LiteralStore.

        A literal store is expected to track occurrences of positive and
        negative literals. Implementations for complex sentences should recurse
        into sub-expressions.
        """
        raise NotImplementedError

    def check_value(self, literal: str, is_true: bool) -> bool:
        """Check if this sentence matches (literal, truth-value).

        Args:
            literal: The name of the atom to check.
            is_true: Whether we expect the literal to be positive (True) or
                     negated (False).

        Returns:
            True if this sentence is the requested literal with the requested
            polarity, False otherwise.
        """
        raise NotImplementedError


    def __repr__(self) -> str:
        """Return a readable string representation of the sentence.

        Concrete subclasses should implement a concise representation for
        debugging and display.
        """
        raise NotImplementedError


class Atom(Sentence):
    def __init__(self, name: str):
        self.name = name

    def evaluate(self, world: Dict[str, bool]) -> bool:
        return world[self.name]

    def collect_atoms(self) -> set[str]:
        return {self.name}

    def get_literal_value(self) -> Tuple[str, bool]:
        return self.name, True

    def eliminate_implications(self):
        return self

    def push_not(self):
        return self

    def distribute(self):
        return self

    def is_literal(self):
        return True

    def collect_literals(self, literal_store: LiteralStore):
        literal_store.add(self.name, True)

    def check_value(self, literal: str, is_true: bool) -> bool:
        return self.name == literal and is_true

    def __repr__(self) -> str:
        return self.name


class Not(Sentence):
    def __init__(self, child: Sentence):
        self.child = child

    def evaluate(self, world: Dict[str, bool]) -> bool:
        return not self.child.evaluate(world)

    def collect_atoms(self) -> set[str]:
        return self.child.collect_atoms()

    def get_literal_value(self) -> Tuple[str, bool]:
        if isinstance(self.child, Atom):
            return self.child.name, False
        raise ValueError("Not is not literal")

    def eliminate_implications(self):
        return Not(self.child.eliminate_implications())

    def push_not(self):
        """Push negation inward using De Morgan rules to reach NNF.
        """
        c = self.child
        if isinstance(c, Atom):
            return self
        if isinstance(c, Not):
            return c.child.push_not()
        if isinstance(c, And):
            return Or(Not(c.left).push_not(), Not(c.right).push_not())
        if isinstance(c, Or):
            return And(Not(c.left).push_not(), Not(c.right).push_not())
        return Not(c.push_not())

    def distribute(self):
        """Negation in NNF does not participate in distribution; return self."""
        return self

    def is_literal(self):
        """A Not node is a literal only if it directly wraps an Atom."""
        return isinstance(self.child, Atom)

    def collect_literals(self, literal_store: LiteralStore):
        """Add this negative literal to the literal store if applicable.

        Raises:
            ValueError: if Not is not a literal after push_not (i.e., still wraps
                        a non-Atom child).
        """
        if isinstance(self.child, Atom):
            literal_store.add(self.child.name, False)
        else:
            raise ValueError("Not is still not literal after push_not")

    def check_value(self, literal: str, is_true: bool) -> bool:
        return isinstance(self.child, Atom) and self.child.name == literal and not is_true

    def __repr__(self) -> str:
        return f"¬({self.child})"


class And(Sentence):
    def __init__(self, left: Sentence, right: Sentence):
        self.left = left
        self.right = right

    def evaluate(self, world: Dict[str, bool]) -> bool:
        return self.left.evaluate(world) and self.right.evaluate(world)

    def collect_atoms(self) -> set[str]:
        return self.left.collect_atoms() | self.right.collect_atoms()

    def eliminate_implications(self):
        """Eliminate implications recursively in both children."""
        return And(self.left.eliminate_implications(), self.right.eliminate_implications())

    def push_not(self):
        """Push negations into both children (NNF)."""
        return And(self.left.push_not(), self.right.push_not())

    def distribute(self):
        """Distribution for conjunction is just distributing into children."""
        return And(self.left.distribute(), self.right.distribute())

    def add_clause(self, sentence):
        """Convenience: append another sentence under a top-level And.

        Returns a new And combining current node and the provided sentence.
        """
        return And(self, sentence)

    def collect_literals(self, literal_store: LiteralStore):
        self.left.collect_literals(literal_store)
        self.right.collect_literals(literal_store)

    def __repr__(self) -> str:
        return f"({self.left} ∧ {self.right})"


class Or(Sentence):
    def __init__(self, left: Sentence, right: Sentence):
        self.left = left
        self.right = right

    def evaluate(self, world: Dict[str, bool]) -> bool:
        return self.left.evaluate(world) or self.right.evaluate(world)

    def collect_atoms(self) -> set[str]:
        return self.left.collect_atoms() | self.right.collect_atoms()

    def eliminate_implications(self):
        """Eliminate implications recursively in both children."""
        return Or(self.left.eliminate_implications(), self.right.eliminate_implications())

    def push_not(self):
        """Push negations into both children (NNF)."""
        return Or(self.left.push_not(), self.right.push_not())

    def distribute(self):
        """Distribute Or over And to reach CNF when needed.

        If either child is an And, perform the standard distribution law to
        return an And of Ors. Otherwise return an Or of distributed children.
        """
        l = self.left.distribute()
        r = self.right.distribute()

        if isinstance(l, And):
            return And(Or(l.left, r).distribute(), Or(l.right, r).distribute())
        if isinstance(r, And):
            return And(Or(l, r.left).distribute(), Or(l, r.right).distribute())
        return Or(l, r)

    def collect_literals(self, literal_store: LiteralStore):
        self.left.collect_literals(literal_store)
        self.right.collect_literals(literal_store)

    def __repr__(self) -> str:
        return f"({self.left} ∨ {self.right})"


class Implies(Sentence):
    def __init__(self, left: Sentence, right: Sentence):
        self.left = left
        self.right = right

    def evaluate(self, world: Dict[str, bool]) -> bool:
        return (not self.left.evaluate(world)) or self.right.evaluate(world)

    def collect_atoms(self) -> set[str]:
        return self.left.collect_atoms() | self.right.collect_atoms()

    def eliminate_implications(self):
        """Rewrite implication as an equivalent disjunction: ¬left ∨ right."""
        return Or(Not(self.left).eliminate_implications(), self.right.eliminate_implications())

    def push_not(self):
        """First eliminate implications, then push negations."""
        return self.eliminate_implications().push_not()

    def distribute(self):
        """Combine elimination and pushing of negation before distribution."""
        return self.push_not().distribute()

    def __repr__(self) -> str:
        """Readable representation for implication."""
        return f"({self.left} → {self.right})"


class Biconditional(Sentence):
    def __init__(self, left: Sentence, right: Sentence):
        self.left = left
        self.right = right

    def evaluate(self, world: Dict[str, bool]) -> bool:
        return self.left.evaluate(world) == self.right.evaluate(world)

    def collect_atoms(self) -> set[str]:
        return self.left.collect_atoms() | self.right.collect_atoms()

    def eliminate_implications(self):
        """Rewrite biconditional as conjunction of two implications."""
        a = self.left
        b = self.right
        return And(Implies(a, b).eliminate_implications(),
                   Implies(b, a).eliminate_implications())

    def push_not(self):
        """Eliminate biconditional first, then push negations."""
        return self.eliminate_implications().push_not()

    def distribute(self):
        return self.push_not().distribute()

    def __repr__(self) -> str:
        return f"({self.left} ↔ {self.right})"

