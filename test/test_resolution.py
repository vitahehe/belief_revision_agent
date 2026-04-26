import pytest
from Sentence import Atom, Not, And, Or, Implies, Biconditional
from KnowledgeBase import KnowledgeBase
from inference.resolution import resolve, resolution_unsat, resolution_entails


def test_resolve_basic():
    c1 = frozenset({"~A", "B"})
    c2 = frozenset({"A"})
    resolvents = resolve(c1, c2)
    assert resolvents == {frozenset({"B"})}


def test_resolution_unsat_tautology():
    clauses = {frozenset({"A"}), frozenset({"~A"})}
    assert resolution_unsat(clauses) == True


def test_resolution_unsat_satisfiable():
    clauses = {frozenset({"A"}), frozenset({"B"})}
    assert resolution_unsat(clauses) == False


def test_resolution_entails_simple():
    kb = KnowledgeBase([Atom("A"), Implies(Atom("A"), Atom("B"))])
    query = Atom("B")
    assert resolution_entails(kb, query) == True


def test_resolution_entails_false():
    kb = KnowledgeBase([Atom("A")])
    query = Atom("B")
    assert resolution_entails(kb, query) == False


def test_resolution_entails_biconditional():
    kb = KnowledgeBase([Biconditional(Atom("A"), Atom("B")), Atom("A")])
    query = Atom("B")
    assert resolution_entails(kb, query) == True


def test_resolution_entails_inconsistent():
    kb = KnowledgeBase([Atom("A"), Not(Atom("A"))])
    query = Atom("B")  # Anything should be entailed from contradiction
    assert resolution_entails(kb, query) == True