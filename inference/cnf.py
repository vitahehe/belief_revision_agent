"""
CNF (Conjunctive Normal Form) conversion for propositional logic formulas.

This module converts arbitrary propositional logic formulas to CNF through
a series of transformations:
  1. eliminate_iff: Remove biconditionals
  2. eliminate_implies: Remove implications
  3. move_not_inwards: Apply De Morgan's laws and double negation elimination
  4. distribute_or_over_and: Distribute OR over AND to achieve CNF

The result is a formula in CNF: a conjunction of disjunctions of literals.
"""

from logic.ast import Formula, Atom, Not, And, Or, Implies, Biconditional


def eliminate_iff(formula: Formula) -> Formula:
    """Eliminate biconditional operators.
    
    Transform A <-> B to (A -> B) & (B -> A).
    
    Args:
        formula: The formula to transform.
    
    Returns:
        An equivalent formula with no Biconditional nodes.
    """
    if isinstance(formula, Biconditional):
        # A <-> B becomes (A -> B) & (B -> A)
        left_to_right = Implies(formula.left, formula.right)
        right_to_left = Implies(formula.right, formula.left)
        return And(
            eliminate_iff(left_to_right),
            eliminate_iff(right_to_left)
        )
    elif isinstance(formula, Implies):
        # Keep implications for now, they'll be eliminated next
        return Implies(
            eliminate_iff(formula.left),
            eliminate_iff(formula.right)
        )
    elif isinstance(formula, And):
        return And(
            eliminate_iff(formula.left),
            eliminate_iff(formula.right)
        )
    elif isinstance(formula, Or):
        return Or(
            eliminate_iff(formula.left),
            eliminate_iff(formula.right)
        )
    elif isinstance(formula, Not):
        return Not(eliminate_iff(formula.child))
    else:
        # Atom
        return formula


def eliminate_implies(formula: Formula) -> Formula:
    """Eliminate implication operators.
    
    Transform A -> B to ~A | B.
    Assumes biconditionals have already been eliminated.
    
    Args:
        formula: The formula to transform.
    
    Returns:
        An equivalent formula with no Implies or Biconditional nodes.
    """
    if isinstance(formula, Implies):
        # A -> B becomes ~A | B
        negated_left = Not(formula.left)
        return Or(
            eliminate_implies(negated_left),
            eliminate_implies(formula.right)
        )
    elif isinstance(formula, And):
        return And(
            eliminate_implies(formula.left),
            eliminate_implies(formula.right)
        )
    elif isinstance(formula, Or):
        return Or(
            eliminate_implies(formula.left),
            eliminate_implies(formula.right)
        )
    elif isinstance(formula, Not):
        return Not(eliminate_implies(formula.child))
    else:
        # Atom
        return formula


def move_not_inwards(formula: Formula) -> Formula:
    """Move negations inward to achieve negation normal form (NNF).
    
    Apply De Morgan's laws and double negation elimination:
      ~~A becomes A
      ~(A & B) becomes ~A | ~B
      ~(A | B) becomes ~A & ~B
    
    After this transformation, Not should only appear directly above Atoms.
    
    Args:
        formula: The formula to transform.
    
    Returns:
        An equivalent formula in NNF.
    """
    if isinstance(formula, Not):
        child = formula.child
        
        # Double negation: ~~A becomes A
        if isinstance(child, Not):
            return move_not_inwards(child.child)
        
        # De Morgan: ~(A & B) becomes ~A | ~B
        elif isinstance(child, And):
            return Or(
                move_not_inwards(Not(child.left)),
                move_not_inwards(Not(child.right))
            )
        
        # De Morgan: ~(A | B) becomes ~A & ~B
        elif isinstance(child, Or):
            return And(
                move_not_inwards(Not(child.left)),
                move_not_inwards(Not(child.right))
            )
        
        # Not should not wrap Implies or Biconditional at this point
        elif isinstance(child, Implies):
            # If we encounter this, transform the implication first
            # A -> B becomes ~A | B, so ~(A -> B) becomes ~(~A | B) = A & ~B
            return move_not_inwards(And(
                child.left,
                Not(child.right)
            ))
        
        elif isinstance(child, Biconditional):
            # Handle if not already eliminated
            # A <-> B becomes (A -> B) & (B -> A)
            # ~(A <-> B) becomes ~((A -> B) & (B -> A)) = ~(A -> B) | ~(B -> A)
            left_to_right = Implies(child.left, child.right)
            right_to_left = Implies(child.right, child.left)
            return Or(
                move_not_inwards(Not(left_to_right)),
                move_not_inwards(Not(right_to_left))
            )
        
        else:
            # Atom - return as is
            return Not(child)
    
    elif isinstance(formula, And):
        return And(
            move_not_inwards(formula.left),
            move_not_inwards(formula.right)
        )
    
    elif isinstance(formula, Or):
        return Or(
            move_not_inwards(formula.left),
            move_not_inwards(formula.right)
        )
    
    else:
        # Atom
        return formula


def distribute_or_over_and(formula: Formula) -> Formula:
    """Distribute OR over AND to achieve CNF.
    
    Transform:
      A | (B & C) becomes (A | B) & (A | C)
      (A & B) | C becomes (A | C) & (B | C)
    
    Recursively applies until the result is in CNF.
    
    Args:
        formula: The formula to transform (should be in NNF).
    
    Returns:
        An equivalent formula in CNF.
    """
    if isinstance(formula, Or):
        left = distribute_or_over_and(formula.left)
        right = distribute_or_over_and(formula.right)
        
        # Case 1: left is And, right is anything
        #   (A & B) | C becomes (A | C) & (B | C)
        if isinstance(left, And):
            return And(
                distribute_or_over_and(Or(left.left, right)),
                distribute_or_over_and(Or(left.right, right))
            )
        
        # Case 2: right is And, left is anything
        #   A | (B & C) becomes (A | B) & (A | C)
        elif isinstance(right, And):
            return And(
                distribute_or_over_and(Or(left, right.left)),
                distribute_or_over_and(Or(left, right.right))
            )
        
        # No And to distribute: just ensure children are distributed
        else:
            return Or(left, right)
    
    elif isinstance(formula, And):
        return And(
            distribute_or_over_and(formula.left),
            distribute_or_over_and(formula.right)
        )
    
    else:
        # Atom or Not(Atom)
        return formula


def to_cnf(formula: Formula) -> Formula:
    """Convert a formula to Conjunctive Normal Form (CNF).
    
    Pipeline:
      1. Eliminate biconditionals
      2. Eliminate implications
      3. Move negations inward (NNF)
      4. Distribute OR over AND
    
    Args:
        formula: The formula to convert.
    
    Returns:
        An equivalent formula in CNF.
    """
    step1 = eliminate_iff(formula)
    step2 = eliminate_implies(step1)
    step3 = move_not_inwards(step2)
    step4 = distribute_or_over_and(step3)
    return step4


def extract_clauses(cnf_formula: Formula) -> set[frozenset[str]]:
    """Extract clauses from a CNF formula.
    
    Converts a CNF formula (consisting of And/Or/Not/Atom nodes) into
    a set of clauses. Each clause is a frozenset of literals (strings).
    
    Literal representation:
      "A" for positive literal
      "~A" for negative literal
    
    Args:
        cnf_formula: A formula in CNF (result of to_cnf).
    
    Returns:
        A set of clauses, where each clause is frozenset[str].
        Tautological clauses (containing both "A" and "~A") are omitted.
    
    Raises:
        ValueError: If the formula is not in valid CNF structure
                   (e.g., Not wraps something other than Atom).
    """
    clauses = set()
    
    def collect_clauses(formula: Formula, clauses_list: list):
        """Recursively collect clauses from CNF formula."""
        if isinstance(formula, And):
            # Top-level conjunction: each child is a clause
            collect_clauses(formula.left, clauses_list)
            collect_clauses(formula.right, clauses_list)
        else:
            # Single clause (Or or literal)
            clause = extract_clause(formula)
            clauses_list.append(clause)
    
    def extract_clause(formula: Formula) -> frozenset[str]:
        """Extract a single clause (disjunction of literals)."""
        literals = []
        
        def collect_literals(f: Formula):
            """Recursively collect literals from a disjunction."""
            if isinstance(f, Or):
                collect_literals(f.left)
                collect_literals(f.right)
            elif isinstance(f, Atom):
                literals.append(f.name)
            elif isinstance(f, Not):
                if not isinstance(f.child, Atom):
                    raise ValueError(
                        f"Invalid CNF: negation does not wrap atom: {f}"
                    )
                literals.append(f"~{f.child.name}")
            else:
                raise ValueError(f"Invalid CNF structure: {f}")
        
        collect_literals(formula)
        clause = frozenset(literals)
        
        # Skip tautological clauses (containing both A and ~A)
        if not is_tautological_clause(clause):
            return clause
        else:
            # Return empty frozenset as marker (will be filtered)
            return frozenset()
    
    clauses_list = []
    collect_clauses(cnf_formula, clauses_list)
    
    # Filter out empty marker frozensets and collect
    for clause in clauses_list:
        if clause:  # Non-empty clause
            clauses.add(clause)
    
    return clauses


def is_tautological_clause(clause: frozenset[str]) -> bool:
    """Check if a clause is tautological (contains both A and ~A).
    
    Args:
        clause: A clause represented as frozenset[str].
    
    Returns:
        True if the clause is tautological.
    """
    for literal in clause:
        if literal.startswith("~"):
            positive = literal[1:]
        else:
            positive = f"~{literal}"
        
        if positive in clause:
            return True
    
    return False
