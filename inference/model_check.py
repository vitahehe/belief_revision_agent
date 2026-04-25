"""
Truth table model checking for entailment (debugging helper only).

This module provides a brute-force truth table approach to entailment checking.
It is useful for verifying resolution results on small examples, but is not
the default entailment method due to exponential complexity.

NOT USED FOR PRODUCTION - use resolution_entails instead.
"""

from itertools import product
from typing import Dict, Set
from logic.ast import Formula, Atom, Not, And, Or, Implies, Biconditional
from logic.utils import get_symbols


def evaluate_formula(formula: Formula, world: Dict[str, bool]) -> bool:
    """Evaluate a formula under a given truth assignment.
    
    Args:
        formula: The formula to evaluate.
        world: A mapping from atom names to boolean values.
    
    Returns:
        The truth value of the formula in the world.
    
    Raises:
        KeyError: If a required atom is not in the world.
    """
    if isinstance(formula, Atom):
        return world[formula.name]
    
    elif isinstance(formula, Not):
        return not evaluate_formula(formula.child, world)
    
    elif isinstance(formula, And):
        return (evaluate_formula(formula.left, world) and 
                evaluate_formula(formula.right, world))
    
    elif isinstance(formula, Or):
        return (evaluate_formula(formula.left, world) or 
                evaluate_formula(formula.right, world))
    
    elif isinstance(formula, Implies):
        return (not evaluate_formula(formula.left, world) or 
                evaluate_formula(formula.right, world))
    
    elif isinstance(formula, Biconditional):
        left_val = evaluate_formula(formula.left, world)
        right_val = evaluate_formula(formula.right, world)
        return left_val == right_val
    
    else:
        raise ValueError(f"Unknown formula type: {type(formula)}")


def truth_table_entails(kb, query: Formula) -> bool:
    """Check if KB entails query using truth table enumeration.
    
    Brute-force method: enumerate all truth assignments and check if
    whenever all KB beliefs are true, the query is also true.
    
    WARNING: Exponential complexity O(2^n) where n is the number of atoms.
    Use only for debugging on small examples.
    
    Args:
        kb: A BeliefBase object.
        query: The formula being queried.
    
    Returns:
        True if KB entails query, False otherwise.
    """
    # Collect all atoms from KB and query
    all_atoms: Set[str] = set()
    
    for belief in kb.list_beliefs():
        all_atoms.update(get_symbols(belief.formula_ast))
    
    all_atoms.update(get_symbols(query))
    
    # If no atoms, handle special cases
    if not all_atoms:
        # All are tautologies or contradictions
        # Check if all KB beliefs are true (or contradictions)
        # and if query is true (or tautology)
        
        # Empty KB entails a formula iff it's a tautology
        kb_consistent = True
        for belief in kb.list_beliefs():
            # Try a world (any world, since no atoms)
            if not evaluate_formula(belief.formula_ast, {}):
                kb_consistent = False
                break
        
        query_true = evaluate_formula(query, {})
        
        if not kb_consistent:
            # Inconsistent KB: entails anything
            return True
        
        return query_true
    
    atom_list = sorted(all_atoms)
    
    # Enumerate all truth assignments
    for values in product([False, True], repeat=len(atom_list)):
        world = dict(zip(atom_list, values))
        
        # Check if all KB beliefs are true in this world
        kb_satisfied = True
        for belief in kb.list_beliefs():
            if not evaluate_formula(belief.formula_ast, world):
                kb_satisfied = False
                break
        
        # If KB is satisfied and query is false, entailment fails
        if kb_satisfied and not evaluate_formula(query, world):
            return False
    
    # All worlds that satisfy KB also satisfy query
    return True
