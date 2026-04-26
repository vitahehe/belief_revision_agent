from Sentence import Sentence, Atom, Not, And, Or, Implies, Biconditional


def eliminate_iff(formula: Sentence) -> Sentence:
    """Eliminate biconditionals by rewriting as conjunction of implications."""
    if isinstance(formula, Biconditional):
        a = formula.left
        b = formula.right
        return And(Implies(a, b), Implies(b, a))
    elif isinstance(formula, (Atom, Not)):
        return formula
    elif isinstance(formula, (And, Or)):
        return type(formula)(eliminate_iff(formula.left), eliminate_iff(formula.right))
    elif isinstance(formula, Implies):
        return Implies(eliminate_iff(formula.left), eliminate_iff(formula.right))
    else:
        raise ValueError(f"Unknown formula type: {type(formula)}")


def eliminate_implies(formula: Sentence) -> Sentence:
    """Eliminate implications by calling the existing method."""
    return formula.eliminate_implications()


def move_not_inwards(formula: Sentence) -> Sentence:
    """Move negations inwards by calling the existing push_not method."""
    return formula.push_not()


def distribute_or_over_and(formula: Sentence) -> Sentence:
    """Distribute OR over AND by calling the existing distribute method."""
    return formula.distribute()


def to_cnf(formula: Sentence) -> Sentence:
    """Convert formula to CNF by calling the existing to_cnf method."""
    return formula.to_cnf()


def is_literal(node: Sentence) -> bool:
    """Check if a node is a literal (Atom or Not(Atom))."""
    return isinstance(node, Atom) or (isinstance(node, Not) and isinstance(node.child, Atom))


def literal_to_string(node: Sentence) -> str:
    """Convert a literal node to string format: 'A' or '~A'."""
    if isinstance(node, Atom):
        return node.name
    elif isinstance(node, Not) and isinstance(node.child, Atom):
        return f"~{node.child.name}"
    else:
        raise ValueError(f"Node is not a literal: {node}")


def extract_clause(node: Sentence) -> frozenset[str]:
    """Extract literals from a clause (OR of literals) into a frozenset[str]."""
    literals = set()
    stack = [node]
    while stack:
        current = stack.pop()
        if is_literal(current):
            literals.add(literal_to_string(current))
        elif isinstance(current, Or):
            stack.append(current.right)
            stack.append(current.left)
        else:
            raise ValueError(f"Non-literal found in clause: {current}")
    return frozenset(literals)


def extract_clauses(cnf_formula: Sentence) -> set[frozenset[str]]:
    """Extract clauses from a CNF formula (AND of clauses) into set[frozenset[str]]."""
    clauses = set()
    stack = [cnf_formula]
    while stack:
        current = stack.pop()
        if is_literal(current) or isinstance(current, Or):
            clauses.add(extract_clause(current))
        elif isinstance(current, And):
            stack.append(current.right)
            stack.append(current.left)
        else:
            raise ValueError(f"Non-CNF structure found: {current}")
    return clauses