import pytest

from KnowledgeBase import KnowledgeBase
from Sentence import Atom, Not, Implies, Or, And, Biconditional

def is_literal(node):
    return isinstance(node, Atom) or (
        isinstance(node, Not) and isinstance(node.child, Atom)
    )


def is_clause(node):
    """
    Clause = OR of literals (or single literal)
    """
    if is_literal(node):
        return True

    if isinstance(node, Or):
        return is_clause(node.left) and is_clause(node.right)

    return False


def is_cnf(node):
    """
    CNF = AND of clauses (or single clause)
    """
    if is_clause(node):
        return True

    if isinstance(node, And):
        return is_cnf(node.left) and is_cnf(node.right)

    return False


def assert_is_cnf_structure(node):
    assert is_cnf(node), f"Not CNF structure: {node}"


def contains_implies(node):
    if isinstance(node, Implies):
        return True
    if isinstance(node, Atom):
        return False
    if isinstance(node, Not):
        return contains_implies(node.child)
    if isinstance(node, (And, Or)):
        return contains_implies(node.left) or contains_implies(node.right)
    return False


def contains_biconditional(node):
    if isinstance(node, Biconditional):
        return True
    if isinstance(node, Atom):
        return False
    if isinstance(node, Not):
        return contains_biconditional(node.child)
    if isinstance(node, (And, Or)):
        return contains_biconditional(node.left) or contains_biconditional(node.right)
    return False


def test_implication_structure():
    kb = KnowledgeBase([
        Implies(Atom("A"), Atom("B"))
    ])

    cnf = kb.convert_to_cnf()

    assert isinstance(cnf, Or)
    assert is_clause(cnf)


def test_biconditional_structure():
    kb = KnowledgeBase([
        Biconditional(Atom("A"), Atom("B"))
    ])

    cnf = kb.convert_to_cnf()

    assert isinstance(cnf, And)
    assert is_clause(cnf.left)
    assert is_clause(cnf.right)


def test_multiple_sentences_top_and():
    kb = KnowledgeBase([
        Implies(Atom("A"), Atom("B")),
        Or(Atom("C"), Atom("D")),
        Atom("E")
    ])

    cnf = kb.convert_to_cnf()

    assert isinstance(cnf, And)
    assert_is_cnf_structure(cnf.left)
    assert_is_cnf_structure(cnf.right)


def test_no_implications_in_cnf():
    kb = KnowledgeBase([
        Implies(Atom("A"), Implies(Atom("B"), Atom("C"))),
        Biconditional(Atom("D"), Atom("E"))
    ])

    cnf = kb.convert_to_cnf()

    assert not contains_implies(cnf)


def test_no_biconditional_in_cnf():
    kb = KnowledgeBase([
        Biconditional(Atom("A"), Atom("B"))
    ])

    cnf = kb.convert_to_cnf()

    assert not contains_biconditional(cnf)


def test_mixed_kb_cnf_structure():
    kb = KnowledgeBase([
        Implies(Atom("A"), Or(Atom("B"), Atom("C"))),
        Biconditional(Atom("D"), Not(Atom("E"))),
        Or(Not(Atom("F")), Atom("G"))
    ])

    cnf = kb.convert_to_cnf()

    assert_is_cnf_structure(cnf)