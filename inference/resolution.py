"""
Propositional resolution algorithm for entailment checking.

Implements the refutation principle: KB entails query iff KB ∧ ~query is unsatisfiable.

Uses the resolution rule: from {A, B} and {~A, C} derive {B, C}.
"""

from typing import Optional, Set
from logic.ast import Formula, Atom, Not
from logic.utils import negate
from inference.cnf import to_cnf, extract_clauses


def negate_literal(lit: str) -> str:
    """Negate a literal string.
    
    Args:
        lit: A literal ("A" or "~A").
    
    Returns:
        The negation of the literal.
    
    Example:
        negate_literal("A") == "~A"
        negate_literal("~A") == "A"
    """
    if lit.startswith("~"):
        return lit[1:]
    else:
        return f"~{lit}"


def are_complementary(lit1: str, lit2: str) -> bool:
    """Check if two literals are complementary.
    
    Args:
        lit1: First literal.
        lit2: Second literal.
    
    Returns:
        True if lit1 and lit2 are complements.
    
    Example:
        are_complementary("A", "~A") == True
        are_complementary("A", "B") == False
    """
    return negate_literal(lit1) == lit2


def is_tautological_clause(clause: frozenset[str]) -> bool:
    """Check if a clause is tautological (contains both A and ~A).
    
    Args:
        clause: A clause represented as frozenset[str].
    
    Returns:
        True if the clause is tautological.
    """
    for literal in clause:
        if negate_literal(literal) in clause:
            return True
    return False


def resolve_pair(
    ci: frozenset[str],
    cj: frozenset[str]
) -> Set[frozenset[str]]:
    """Resolve two clauses using the resolution rule.
    
    For each complementary literal pair between ci and cj:
      - Remove the complementary pair
      - Union the remaining literals
      - Add the resulting clause
    
    Args:
        ci: First clause.
        cj: Second clause.
    
    Returns:
        A set of resolvents. Empty set if no complementary pairs exist.
        Excludes tautological resolvents.
    
    Example:
        resolve_pair({"A", "B"}, {"~A", "C"}) returns {frozenset({"B", "C"})}
    """
    resolvents = set()
    
    for lit_i in ci:
        for lit_j in cj:
            if are_complementary(lit_i, lit_j):
                # Resolve on this complementary pair
                remaining = (ci - {lit_i}) | (cj - {lit_j})
                
                # Skip tautological resolvents
                if not is_tautological_clause(remaining):
                    resolvents.add(remaining)
    
    return resolvents


def resolution_unsat(clauses: Set[frozenset[str]]) -> bool:
    """Determine if a clause set is unsatisfiable using resolution.
    
    Algorithm:
      1. Start with the initial clause set
      2. Repeatedly resolve every pair of distinct clauses
      3. If the empty clause is derived, return True (unsatisfiable)
      4. If no new clauses are produced, return False (satisfiable)
      5. Maintain a set of processed clause pairs to guarantee termination
    
    Args:
        clauses: A set of clauses to check.
    
    Returns:
        True if the clause set is unsatisfiable (derivable: empty clause).
        False if the clause set is satisfiable.
    """
    # Start with the initial clause set
    known_clauses = set(clauses)
    
    # Track pairs already resolved to avoid redundant work
    processed_pairs = set()
    
    # Convert to list for indexing
    clause_list = list(known_clauses)
    
    while True:
        new_clauses = set()
        
        # Try to resolve every pair of clauses
        for i, ci in enumerate(clause_list):
            for j, cj in enumerate(clause_list):
                if i >= j:  # Only resolve each pair once
                    continue
                
                # Create a hashable pair identifier
                pair_id = (frozenset(ci), frozenset(cj))
                if pair_id in processed_pairs:
                    continue
                
                processed_pairs.add(pair_id)
                
                # Try to resolve
                resolvents = resolve_pair(ci, cj)
                
                # Check for empty clause
                for resolvent in resolvents:
                    if len(resolvent) == 0:
                        # Empty clause found: unsatisfiable
                        return True
                    
                    if resolvent not in known_clauses:
                        new_clauses.add(resolvent)
        
        # If no new clauses, we've reached a fixed point
        if not new_clauses:
            return False
        
        # Add new clauses and continue
        known_clauses.update(new_clauses)
        clause_list = list(known_clauses)


def resolution_entails(kb, query: Formula) -> bool:
    """Check if the knowledge base entails the query using resolution.
    
    Implements the refutation principle:
      KB entails query iff KB ∧ ~query is unsatisfiable
    
    Algorithm:
      1. Collect all belief formulas from the KB
      2. Convert each to CNF and extract clauses
      3. Negate the query and convert to CNF and extract clauses
      4. Combine all clauses
      5. Check if the combined set is unsatisfiable using resolution
    
    Args:
        kb: A BeliefBase object containing the knowledge base.
        query: The formula being queried.
    
    Returns:
        True if KB entails query, False otherwise.
    
    Important behavior:
      - Does not mutate the KB or any formulas
      - If KB is inconsistent, returns True for any query (explosion principle)
      - If KB is empty, only returns True for tautologies
    """
    # Collect all clauses from the KB beliefs
    all_clauses = set()
    
    for belief in kb.list_beliefs():
        formula_ast = belief.formula_ast
        # Convert to CNF
        cnf_formula = to_cnf(formula_ast)
        # Extract clauses
        clauses = extract_clauses(cnf_formula)
        all_clauses.update(clauses)
    
    # Negate the query and convert to CNF
    negated_query = negate(query)
    cnf_negated_query = to_cnf(negated_query)
    query_clauses = extract_clauses(cnf_negated_query)
    
    # Combine all clauses
    combined_clauses = all_clauses | query_clauses
    
    # Check if unsatisfiable
    return resolution_unsat(combined_clauses)
