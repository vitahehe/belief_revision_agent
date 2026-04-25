"""
Abstract Syntax Tree (AST) for propositional logic formulas.

This module defines immutable AST node classes representing propositional logic formulas.
All nodes are frozen dataclasses to ensure immutability.
"""

from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class Formula:
    """Base class for all formula nodes. Frozen to ensure immutability."""
    pass


@dataclass(frozen=True)
class Atom(Formula):
    """An atomic proposition (propositional variable).
    
    Args:
        name: The symbol name of the atom (e.g., 'P', 'Q', 'Raining').
    """
    name: str

    def __repr__(self) -> str:
        return self.name


@dataclass(frozen=True)
class Not(Formula):
    """Negation of a formula.
    
    Args:
        child: The formula being negated.
    """
    child: Formula

    def __repr__(self) -> str:
        return f"~{self.child}"


@dataclass(frozen=True)
class And(Formula):
    """Conjunction of two formulas.
    
    Args:
        left: The left conjunct.
        right: The right conjunct.
    """
    left: Formula
    right: Formula

    def __repr__(self) -> str:
        return f"({self.left} & {self.right})"


@dataclass(frozen=True)
class Or(Formula):
    """Disjunction of two formulas.
    
    Args:
        left: The left disjunct.
        right: The right disjunct.
    """
    left: Formula
    right: Formula

    def __repr__(self) -> str:
        return f"({self.left} | {self.right})"


@dataclass(frozen=True)
class Implies(Formula):
    """Material implication (conditional) between two formulas.
    
    Args:
        left: The antecedent (premise).
        right: The consequent (conclusion).
    """
    left: Formula
    right: Formula

    def __repr__(self) -> str:
        return f"({self.left} -> {self.right})"


@dataclass(frozen=True)
class Biconditional(Formula):
    """Biconditional (equivalence) between two formulas.
    
    Args:
        left: The left formula.
        right: The right formula.
    """
    left: Formula
    right: Formula

    def __repr__(self) -> str:
        return f"({self.left} <-> {self.right})"
