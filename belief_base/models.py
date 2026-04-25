"""
Belief model for the belief base system.

A Belief represents a single propositional logic formula stored in the belief base,
along with metadata for tracking insertion order and priority.
"""

from dataclasses import dataclass
from logic.ast import Formula


@dataclass(frozen=True)
class Belief:
    """A belief held in the belief base.
    
    Attributes:
        id: Unique identifier for this belief (typically a UUID or counter).
        formula_str: The original string representation of the formula as provided by the user.
        normalized_formula_str: Normalized string representation used for duplicate detection.
        formula_ast: The Abstract Syntax Tree representation of the formula.
        priority: Priority level indicating entrenchment. Higher values are more entrenched
                 and harder to remove during contraction. Lower values are easier to remove.
        insertion_order: The order in which this belief was inserted into the base (monotonically increasing).
    """
    id: str
    formula_str: str
    normalized_formula_str: str
    formula_ast: Formula
    priority: int
    insertion_order: int

    def __repr__(self) -> str:
        return f"Belief(id={self.id}, formula={self.formula_str}, priority={self.priority}, order={self.insertion_order})"
