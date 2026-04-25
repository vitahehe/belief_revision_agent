"""
Belief Base system for managing propositional logic beliefs.

The BeliefBase provides:
- Storage and management of beliefs with priority levels
- Duplicate detection based on normalized formula strings
- Deterministic insertion order tracking
- Copy-on-write semantics to preserve immutability of the base
"""

from typing import List, Optional, Dict
import uuid
from logic.parser import parse, ParseError
from logic.utils import formula_to_string, normalize_formula
from belief_base.models import Belief


class BeliefBase:
    """Manages a collection of beliefs with priorities and insertion order.
    
    The belief base ensures:
    - No duplicate formulas (checked via normalized representation)
    - Deterministic insertion order tracking
    - Priority-based entrenchment (higher priority = harder to remove)
    - Ability to copy without mutations affecting the original
    """
    
    def __init__(self):
        """Initialize an empty belief base."""
        self._beliefs: Dict[str, Belief] = {}  # Map from belief id to Belief
        self._normalized_to_id: Dict[str, str] = {}  # Map from normalized formula to belief id
        self._next_insertion_order: int = 0  # Counter for deterministic insertion order
    
    def create_belief(
        self,
        formula_text: str,
        priority: int = 0,
        insertion_order: Optional[int] = None
    ) -> Belief:
        """Create a Belief object from a formula string.
        
        Args:
            formula_text: The propositional logic formula string (e.g., "A & B").
            priority: The priority level of this belief (default 0). Higher values are
                     more entrenched and harder to remove.
            insertion_order: The insertion order (auto-assigned if None).
        
        Returns:
            A new Belief object.
        
        Raises:
            ParseError: If the formula string is invalid.
        """
        formula_ast = parse(formula_text)
        normalized = normalize_formula(formula_ast)
        
        if insertion_order is None:
            insertion_order = self._next_insertion_order
            self._next_insertion_order += 1
        else:
            # Update counter if explicit insertion_order is provided
            if insertion_order >= self._next_insertion_order:
                self._next_insertion_order = insertion_order + 1
        
        belief_id = str(uuid.uuid4())
        
        return Belief(
            id=belief_id,
            formula_str=formula_text,
            normalized_formula_str=normalized,
            formula_ast=formula_ast,
            priority=priority,
            insertion_order=insertion_order
        )
    
    def add_belief(self, belief: Belief) -> bool:
        """Add a belief to the base.
        
        Args:
            belief: The Belief to add.
        
        Returns:
            True if the belief was added, False if a duplicate formula already exists.
        
        Raises:
            ValueError: If the belief's id is already in the base.
        """
        # Check for duplicate formula
        if belief.normalized_formula_str in self._normalized_to_id:
            return False
        
        # Check for duplicate id
        if belief.id in self._beliefs:
            raise ValueError(f"Belief with id {belief.id} already exists in the base")
        
        # Add the belief
        self._beliefs[belief.id] = belief
        self._normalized_to_id[belief.normalized_formula_str] = belief.id
        
        # Update insertion order counter
        if belief.insertion_order >= self._next_insertion_order:
            self._next_insertion_order = belief.insertion_order + 1
        
        return True
    
    def remove_belief_by_id(self, belief_id: str) -> bool:
        """Remove a belief from the base by its id.
        
        Args:
            belief_id: The id of the belief to remove.
        
        Returns:
            True if the belief was removed, False if it doesn't exist.
        """
        if belief_id not in self._beliefs:
            return False
        
        belief = self._beliefs[belief_id]
        del self._beliefs[belief_id]
        del self._normalized_to_id[belief.normalized_formula_str]
        return True
    
    def list_beliefs(self) -> List[Belief]:
        """Get all beliefs in the base, sorted by insertion order.
        
        Returns:
            A list of all beliefs, deterministically ordered by insertion time.
        """
        return sorted(self._beliefs.values(), key=lambda b: b.insertion_order)
    
    def contains_formula(self, formula_text: str) -> bool:
        """Check if a formula (in normalized form) exists in the base.
        
        Args:
            formula_text: The formula string to check.
        
        Returns:
            True if an equivalent formula exists in the base.
        
        Raises:
            ParseError: If the formula string is invalid.
        """
        formula_ast = parse(formula_text)
        normalized = normalize_formula(formula_ast)
        return normalized in self._normalized_to_id
    
    def copy_kb(self) -> "BeliefBase":
        """Create a deep copy of this belief base.
        
        The copy is independent: modifications to the copy do not affect the original.
        
        Returns:
            A new BeliefBase with the same beliefs.
        """
        copied = BeliefBase()
        # Copy all beliefs (which are immutable)
        for belief in self.list_beliefs():
            copied.add_belief(belief)
        return copied
    
    def get_belief_by_id(self, belief_id: str) -> Optional[Belief]:
        """Get a belief by its id.
        
        Args:
            belief_id: The id of the belief.
        
        Returns:
            The Belief object, or None if not found.
        """
        return self._beliefs.get(belief_id)
    
    def get_belief_by_formula(self, formula_text: str) -> Optional[Belief]:
        """Get a belief by its formula string.
        
        Args:
            formula_text: The formula string to search for.
        
        Returns:
            The Belief object with equivalent formula, or None if not found.
        
        Raises:
            ParseError: If the formula string is invalid.
        """
        formula_ast = parse(formula_text)
        normalized = normalize_formula(formula_ast)
        belief_id = self._normalized_to_id.get(normalized)
        if belief_id:
            return self._beliefs[belief_id]
        return None
    
    def size(self) -> int:
        """Get the number of beliefs in the base.
        
        Returns:
            The count of beliefs.
        """
        return len(self._beliefs)
    
    def __repr__(self) -> str:
        beliefs_repr = "\n  ".join(repr(b) for b in self.list_beliefs())
        return f"BeliefBase({self.size()} beliefs):\n  {beliefs_repr}"
