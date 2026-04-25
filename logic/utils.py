"""
Utility functions for working with propositional logic formulas.

Provides functions for:
- Converting formulas to strings
- Extracting symbols from formulas
- Negating formulas
- Normalizing formulas for comparison
"""

from logic.ast import Formula, Atom, Not, And, Or, Implies, Biconditional


def formula_to_string(formula: Formula) -> str:
    """Convert a formula AST to a string representation.
    
    Args:
        formula: The formula to convert.
    
    Returns:
        A string representation of the formula.
    """
    if isinstance(formula, Atom):
        return formula.name
    elif isinstance(formula, Not):
        return f"~{formula_to_string(formula.child)}"
    elif isinstance(formula, And):
        left_str = formula_to_string(formula.left)
        right_str = formula_to_string(formula.right)
        return f"({left_str} & {right_str})"
    elif isinstance(formula, Or):
        left_str = formula_to_string(formula.left)
        right_str = formula_to_string(formula.right)
        return f"({left_str} | {right_str})"
    elif isinstance(formula, Implies):
        left_str = formula_to_string(formula.left)
        right_str = formula_to_string(formula.right)
        return f"({left_str} -> {right_str})"
    elif isinstance(formula, Biconditional):
        left_str = formula_to_string(formula.left)
        right_str = formula_to_string(formula.right)
        return f"({left_str} <-> {right_str})"
    else:
        raise ValueError(f"Unknown formula type: {type(formula)}")


def get_symbols(formula: Formula) -> set[str]:
    """Extract all atomic proposition symbols from a formula.
    
    Args:
        formula: The formula to analyze.
    
    Returns:
        A set of symbol names appearing in the formula.
    """
    if isinstance(formula, Atom):
        return {formula.name}
    elif isinstance(formula, Not):
        return get_symbols(formula.child)
    elif isinstance(formula, (And, Or, Implies, Biconditional)):
        left_symbols = get_symbols(formula.left)
        right_symbols = get_symbols(formula.right)
        return left_symbols | right_symbols
    else:
        raise ValueError(f"Unknown formula type: {type(formula)}")


def negate(formula: Formula) -> Formula:
    """Return the negation of a formula.
    
    Simplifies double negation (~~A becomes A).
    
    Args:
        formula: The formula to negate.
    
    Returns:
        The negation of the formula, with double negation simplified.
    """
    if isinstance(formula, Not):
        # Simplify double negation
        return formula.child
    else:
        return Not(formula)


def normalize_formula(formula: Formula) -> str:
    """Normalize a formula to a canonical string representation.
    
    This is used for checking duplicates in the belief base.
    The normalized form:
    - Removes unnecessary parentheses
    - Uses consistent spacing
    - Preserves the logical structure for comparison
    
    Args:
        formula: The formula to normalize.
    
    Returns:
        A normalized string representation.
    """
    return _normalize_helper(formula, parent_precedence=6)


def _normalize_helper(formula: Formula, parent_precedence: int = 6) -> str:
    """Helper function for recursive normalization with precedence handling.
    
    Precedence levels (higher number = higher precedence, so tighter binding):
    1. <-> (biconditional, lowest)
    2. -> (implication)
    3. | (disjunction)
    4. & (conjunction)
    5. ~ (negation)
    6. atoms (highest)
    
    Args:
        formula: The formula to normalize.
        parent_precedence: Precedence of the parent operator.
    
    Returns:
        A normalized string representation.
    """
    if isinstance(formula, Atom):
        return formula.name
    
    elif isinstance(formula, Not):
        # Negation has precedence 5
        child_str = _normalize_helper(formula.child, parent_precedence=5)
        return f"~{child_str}"
    
    elif isinstance(formula, And):
        # Conjunction has precedence 4
        current_precedence = 4
        left_str = _normalize_helper(formula.left, parent_precedence=current_precedence)
        right_str = _normalize_helper(formula.right, parent_precedence=current_precedence)
        result = f"{left_str} & {right_str}"
        if current_precedence < parent_precedence:
            result = f"({result})"
        return result
    
    elif isinstance(formula, Or):
        # Disjunction has precedence 3
        current_precedence = 3
        left_str = _normalize_helper(formula.left, parent_precedence=current_precedence)
        right_str = _normalize_helper(formula.right, parent_precedence=current_precedence)
        result = f"{left_str} | {right_str}"
        if current_precedence < parent_precedence:
            result = f"({result})"
        return result
    
    elif isinstance(formula, Implies):
        # Implication has precedence 2
        current_precedence = 2
        left_str = _normalize_helper(formula.left, parent_precedence=current_precedence + 1)
        right_str = _normalize_helper(formula.right, parent_precedence=current_precedence)
        result = f"{left_str} -> {right_str}"
        if current_precedence < parent_precedence:
            result = f"({result})"
        return result
    
    elif isinstance(formula, Biconditional):
        # Biconditional has precedence 1 (lowest)
        current_precedence = 1
        left_str = _normalize_helper(formula.left, parent_precedence=current_precedence + 1)
        right_str = _normalize_helper(formula.right, parent_precedence=current_precedence + 1)
        result = f"{left_str} <-> {right_str}"
        if current_precedence < parent_precedence:
            result = f"({result})"
        return result
    
    else:
        raise ValueError(f"Unknown formula type: {type(formula)}")
