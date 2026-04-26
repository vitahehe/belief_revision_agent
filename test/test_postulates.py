import pytest

from Sentence import Atom, Not, Implies
from KnowledgeBase import KnowledgeBase, BeliefEntry
from inference.resolution import resolution_unsat


def is_consistent(kb: KnowledgeBase) -> bool:
    """KB consistency = its clause-set is satisfiable."""
    return not resolution_unsat(kb.to_clause_set())


def test_contraction_success_postulate():
    # If KB entails phi and phi is not a tautology, then after contracting phi,
    # KB should no longer entail phi.
    a = Atom("A")
    kb = KnowledgeBase([a])
    assert kb.entails(a) is True

    new_kb, removed = kb.contract(a)
    assert new_kb.entails(a) is False
    assert len(removed) >= 1


def test_contraction_inclusion_postulate():
    a = Atom("A")
    a_implies_b = Implies(Atom("A"), Atom("B"))
    entries = [
        BeliefEntry(belief_id="b1", sentence=a, priority=2, insertion_order=0),
        BeliefEntry(belief_id="b2", sentence=a_implies_b, priority=1, insertion_order=1),
    ]
    kb = KnowledgeBase(entries=entries)

    new_kb, _ = kb.contract(Atom("B"))
    old_ids = {e.id for e in kb.entries}
    new_ids = {e.id for e in new_kb.entries}
    assert new_ids.issubset(old_ids)


def test_contraction_vacuity_postulate():
    kb = KnowledgeBase([Atom("A")])
    phi = Atom("B")
    assert kb.entails(phi) is False

    new_kb, removed = kb.contract(phi)
    assert removed == []
    assert [e.id for e in new_kb.entries] == [e.id for e in kb.entries]


def test_contraction_extensionality_postulate_simple_equivalence():
    # A and ~~A are logically equivalent in propositional logic.
    kb = KnowledgeBase([Atom("A")])

    phi = Atom("A")
    psi = Not(Not(Atom("A")))

    kb1, _ = kb.contract(phi)
    kb2, _ = kb.contract(psi)

    assert [e.normalized_formula_str for e in kb1.entries] == [e.normalized_formula_str for e in kb2.entries]


def test_revision_success_postulate():
    kb = KnowledgeBase([Atom("A")])
    new_kb, removed, added = kb.revise(Atom("B"), priority=3)
    assert new_kb.entails(Atom("B")) is True
    assert added is not None


def test_revision_vacuity_like_behavior_when_no_conflict():
    # If KB does not entail ~phi, revision should behave like adding phi.
    kb = KnowledgeBase([Atom("A")])
    phi = Atom("B")

    assert kb.entails(Not(phi)) is False
    revised, removed, _ = kb.revise(phi, priority=1)
    assert removed == []
    assert revised.entails(phi) is True


def test_revision_consistency_postulate_when_inputs_consistent():
    kb = KnowledgeBase([Atom("A")])
    assert is_consistent(kb)

    phi = Atom("B")
    revised, _, _ = kb.revise(phi, priority=1)
    assert is_consistent(revised)


def test_revision_extensionality_postulate_simple_equivalence():
    kb = KnowledgeBase([Atom("A")])

    phi = Atom("B")
    psi = Not(Not(Atom("B")))

    kb1, _, _ = kb.revise(phi, priority=1)
    kb2, _, _ = kb.revise(psi, priority=1)

    # Extensionality is about logical equivalence, not syntactic identity of stored bases.
    # Both results should entail both equivalent formulations.
    assert kb1.entails(phi) and kb1.entails(psi)
    assert kb2.entails(phi) and kb2.entails(psi)
    # And preserve the original belief A.
    assert kb1.entails(Atom("A")) and kb2.entails(Atom("A"))

