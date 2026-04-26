import pytest
from Sentence import Atom, Not, And, Or, Implies, Biconditional
from inference.cnf import eliminate_implies, to_cnf, extract_clauses


def test_atom_extract():
    a = Atom("A")
    clauses = extract_clauses(a)
    assert clauses == {frozenset({"A"})}


def test_not_atom_extract():
    na = Not(Atom("A"))
    clauses = extract_clauses(na)
    assert clauses == {frozenset({"~A"})}


def test_implies_extract():
    imp = Implies(Atom("A"), Atom("B"))
    cnf = to_cnf(imp)
    clauses = extract_clauses(cnf)
    assert clauses == {frozenset({"~A", "B"})}


def test_biconditional_extract():
    bic = Biconditional(Atom("A"), Atom("B"))
    cnf = to_cnf(bic)
    clauses = extract_clauses(cnf)
    expected = {frozenset({"~A", "B"}), frozenset({"~B", "A"})}
    assert clauses == expected


def test_and_or_extract():
    formula = And(Atom("A"), Or(Not(Atom("A")), Atom("B")))
    cnf = to_cnf(formula)
    clauses = extract_clauses(cnf)
    expected = {frozenset({"A"}), frozenset({"~A", "B"})}
    assert clauses == expected