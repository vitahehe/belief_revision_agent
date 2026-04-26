from Sentence import Not
from inference.cnf import to_cnf, extract_clauses


def complementary_literal(lit: str) -> str:
    """Return the complement of a literal."""
    if lit.startswith("~"):
        return lit[1:]
    else:
        return f"~{lit}"


def are_complementary(a: str, b: str) -> bool:
    """Check if two literals are complementary."""
    return complementary_literal(a) == b


def resolve(ci: frozenset[str], cj: frozenset[str]) -> set[frozenset[str]]:
    """Resolve two clauses and return the set of resolvents."""
    resolvents = set()
    for lit_i in ci:
        for lit_j in cj:
            if are_complementary(lit_i, lit_j):
                # Remove the complementary literals
                new_clause = (ci - {lit_i}) | (cj - {lit_j})
                resolvents.add(frozenset(new_clause))
    return resolvents


def resolution_unsat(clauses: set[frozenset[str]]) -> bool:
    """Check if the set of clauses is unsatisfiable using resolution."""
    return _resolution_unsat_recursive(clauses, set())


def _resolution_unsat_recursive(clauses: set[frozenset[str]], seen: set[frozenset[str]]) -> bool:
    """Recursive helper for resolution unsatisfiability check."""
    # Check if empty clause is already present
    if frozenset() in clauses:
        return True

    # Generate all possible resolvents
    new_resolvents = set()
    clause_list = list(clauses)
    for i in range(len(clause_list)):
        for j in range(i + 1, len(clause_list)):
            resolvents = resolve(clause_list[i], clause_list[j])
            for res in resolvents:
                if res not in clauses and res not in seen:
                    new_resolvents.add(res)
                    if not res:  # Empty clause
                        return True

    # If no new resolvents, not unsatisfiable
    if not new_resolvents:
        return False

    # Recurse with new clauses
    return _resolution_unsat_recursive(clauses | new_resolvents, seen | new_resolvents)


def _sentences_from_kb(kb) -> list:
    """Extract sentences from knowledge base."""
    if hasattr(kb, "sentences"):
        return kb.sentences
    elif hasattr(kb, "get_sentences"):
        return kb.get_sentences()
    elif hasattr(kb, "entries"):
        return [entry.sentence or entry.formula_ast for entry in kb.entries]
    else:
        raise ValueError("Unsupported knowledge base format")


def resolution_entails(kb, query) -> bool:
    """Check if KB entails query using resolution."""
    sentences = _sentences_from_kb(kb)
    all_clauses = set()

    # Convert KB sentences to CNF and extract clauses
    for sent in sentences:
        cnf = to_cnf(sent)
        clauses = extract_clauses(cnf)
        all_clauses.update(clauses)

    # Add clauses from ~query
    neg_query = Not(query)
    neg_cnf = to_cnf(neg_query)
    neg_clauses = extract_clauses(neg_cnf)
    all_clauses.update(neg_clauses)

    # Check if unsatisfiable
    return resolution_unsat(all_clauses)